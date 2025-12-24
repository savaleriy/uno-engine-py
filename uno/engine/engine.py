from __future__ import annotations

import random
from enum import Enum
from typing import Dict, List, Optional

from ..player.player import Player
from .card import Card, CardColor, CardLabel
from .deck import Deck


class GameState(Enum):
    """Enum for game states"""

    WAITING_FOR_PLAYERS = "waiting_for_players"
    DEALING_CARDS = "dealing_cards"
    IN_PROGRESS = "in_progress"
    ROUND_OVER = "round_over"
    GAME_OVER = "game_over"


class GameDirection(Enum):
    """Enum for game direction"""

    CLOCKWISE = 1
    COUNTER_CLOCKWISE = -1


class UnoGameEngine:
    """
    UNO Game Engine that manages game state, players, and core game logic
    """

    def __init__(
        self,
        auto_play: bool = True,
        turn_delay: float = 1.0,
        endless_reshuffle: bool = True,
    ):
        self.deck = Deck()
        self.discard_pile: List[Card] = []
        self.players: List[Player] = []
        self.current_player_index: int = 0
        self.game_direction: GameDirection = GameDirection.CLOCKWISE
        self.current_color: Optional[CardColor] = None
        self.game_state: GameState = GameState.WAITING_FOR_PLAYERS
        self.scores: Dict[int, int] = {}  # player_id -> score
        self._starting_player_index: Optional[int] = None
        self.auto_play = auto_play
        self.turn_delay = turn_delay
        self.turn_count = 0
        self.max_turns = 1000
        self.endless_reshuffle = endless_reshuffle

    def add_player(self, player: Player) -> None:
        """
        Add a player to the game
        """
        if self.game_state != GameState.WAITING_FOR_PLAYERS:
            raise ValueError("Cannot add players after game has started")

        if len(self.players) >= 10:  # Reasonable max players
            raise ValueError("Maximum number of players reached")

        self.players.append(player)
        self.scores[player.player_id] = 0

    def initialize_game(self) -> None:
        """
        Initialize the game - deal cards and choose starting player
        """
        if len(self.players) < 2:
            raise ValueError("Need at least 2 players to start the game")

        # Reset game state
        self.game_state = GameState.DEALING_CARDS
        self.discard_pile.clear()
        self.turn_count = 0

        # Re-shuffle deck if needed
        if self.deck.size() < 80:  # If deck has been used before
            self.deck = Deck()  # Create fresh deck

        # Deal initial cards (4 cards per player in standard UNO)
        self._deal_initial_cards(7)

        # Setup discard pile with first card
        self._setup_discard_pile()

        # Choose random starting player
        self._choose_starting_player()

        # Update game state
        self.game_state = GameState.IN_PROGRESS

    def _deal_initial_cards(self, cards_per_player: int = 7) -> None:
        """
        Deal initial cards to all players
        """

        for player in self.players:
            try:
                cards = self.deck.draw(cards_per_player)
                player.add_cards_to_hand(cards)
            except ValueError as e:
                # Handle case where deck doesn't have enough cards
                raise ValueError(
                    f"Not enough cards in deck to deal {cards_per_player} to each player"
                ) from e

    def _setup_discard_pile(self) -> None:
        """
        Setup the discard pile with the first card from deck
        Ensure first card is not a wild or action card
        """
        while True:
            if self.deck.is_empty():
                if self.endless_reshuffle:
                    # Reshuffle if deck is empty (shouldn't happen initially)
                    self._reshuffle_discard_pile()
                else:
                    raise ValueError("Deck is empty and reshuffling is disabled")

            first_card = self.deck.draw(1)[0]

            # If first card is wild or action, put it back and draw another
            if first_card.is_wild or first_card.is_action_card:
                self.deck.add_card(first_card)
                self.deck.shuffle()
            else:
                self.discard_pile.append(first_card)
                self.current_color = first_card.color
                break

    def _choose_starting_player(self) -> None:
        """
        Choose a random player to start the game
        """
        self._starting_player_index = random.randint(0, len(self.players) - 1)
        self.current_player_index = self._starting_player_index

    def _reshuffle_discard_pile(self) -> None:
        """
        Reshuffle the discard pile into the deck when deck is empty
        Keep only the top card on discard pile
        """
        if len(self.discard_pile) <= 1:
            raise ValueError("Not enough cards to reshuffle")

        # Keep the top card on discard pile
        top_card = self.discard_pile[-1]

        # Shuffle the rest back into deck
        cards_to_reshuffle = self.discard_pile[:-1]
        self.deck.add_cards(cards_to_reshuffle)
        self.deck.shuffle()

        # Reset discard pile with just the top card
        self.discard_pile = [top_card]

    def get_current_player(self) -> Player:
        """
        Get the current player
        """
        return self.players[self.current_player_index]

    def get_top_discard_card(self) -> Card:
        """
        Get the top card from discard pile
        """
        if not self.discard_pile:
            raise ValueError("Discard pile is empty")
        return self.discard_pile[-1]

    def get_playable_cards(self, player: Player) -> List[Card]:
        """
        Get list of playable cards for a player
        """
        top_card = self.get_top_discard_card()
        playable_cards = []

        for card in player.hand:
            if card.can_play_on(top_card, self.current_color):
                playable_cards.append(card)

        return playable_cards

    def next_turn(self) -> None:
        """
        Move to next player's turn based on game direction
        """
        if self.game_direction == GameDirection.CLOCKWISE:
            self.current_player_index = (self.current_player_index + 1) % len(
                self.players
            )
        else:
            self.current_player_index = (self.current_player_index - 1) % len(
                self.players
            )

    def reverse_direction(self) -> None:
        """
        Reverse the game direction
        """
        self.game_direction = (
            GameDirection.COUNTER_CLOCKWISE
            if self.game_direction == GameDirection.CLOCKWISE
            else GameDirection.CLOCKWISE
        )

    def play_card(
        self, player: Player, card: Card, new_color: Optional[CardColor] = None
    ) -> Dict:
        """
        Play a card from player's hand
        """
        if card not in player.hand:
            raise ValueError(f"Card {card} not in player's hand")

        # Verify card can be played
        top_card = self.get_top_discard_card()
        if not card.can_play_on(top_card, self.current_color):
            raise ValueError(
                f"Card {card} cannot be played on {top_card} with current color {self.current_color}"
            )

        # Remove card from player's hand and add to discard pile
        player.play_card(card, new_color)
        self.discard_pile.append(card)

        # Handle card effects
        effects = card.play(new_color)

        # Update current color if wild card
        if new_color:
            self.current_color = new_color
        elif card.color != CardColor.WILD:
            self.current_color = card.color

        return effects

    def check_winner(self) -> Optional[Player]:
        """
        Check if there's a winner (player with no cards)
        """
        for player in self.players:
            if player.has_won():
                return player
        return None

    def draw_card(self, player: Player) -> Card:
        """
        Make a player draw a card from deck
        """
        if self.deck.is_empty():
            if self.endless_reshuffle:
                try:
                    self._reshuffle_discard_pile()
                except ValueError as e:
                    # Handle the case where we can't reshuffle (not enough cards)
                    self.game_state = GameState.ROUND_OVER
                    # Return a dummy card or handle this case
                    raise e  # Re-raise to let calling code handle it
            else:
                # No reshuffling allowed - game ends when deck is empty
                self.game_state = GameState.ROUND_OVER
                raise ValueError("Deck is empty and reshuffling is disabled")

        drawn_card = self.deck.draw(1)[0]
        player.add_card_to_hand(drawn_card)

        return drawn_card

    def play_turn(self) -> bool:
        """
        Play one turn for the current player
        Returns True if game should continue, False if game over
        """
        if self.turn_count >= self.max_turns:
            self._end_game_with_scores()
            return False

        self.turn_count += 1
        current_player = self.get_current_player()

        try:
            # Get playable cards for the current player
            playable_cards = self.get_playable_cards(current_player)

            if hasattr(current_player, "update_game_state"):
                current_player.update_game_state(
                    playable_cards, self.get_top_discard_card(), self.current_color
                )

            # Let player choose action
            action = current_player.choose_action()

            if action.draw_card:
                # Player chooses to draw a card
                drawn_card = self.draw_card(current_player)

                # Check if drawn card can be played immediately
                if drawn_card.can_play_on(
                    self.get_top_discard_card(), self.current_color
                ):
                    if hasattr(
                        current_player, "should_play_drawn_card"
                    ) and current_player.should_play_drawn_card(drawn_card):
                        self.play_card(current_player, drawn_card)

            elif action.card:
                # Player plays a card
                try:
                    effects = self.play_card(
                        current_player, action.card, action.new_color
                    )

                    # Handle card effects
                    if action.card.label == CardLabel.REVERSE:
                        self.reverse_direction()
                    elif action.card.label == CardLabel.SKIP:
                        self.next_turn()  # Skip next player
                    elif action.card.label in [
                        CardLabel.DRAW_TWO,
                        CardLabel.WILD_DRAW_FOUR,
                    ]:
                        # For now, just log the draw effect - you can implement drawing later
                        draw_count = 2 if action.card.label == CardLabel.DRAW_TWO else 4

                except ValueError as e:
                    try:
                        self.draw_card(current_player)
                    except ValueError:
                        # If we can't draw, end the game
                        self._end_game_with_scores()
                        return False

            # Check for UNO
            if current_player.has_uno() and current_player.decide_say_uno():
                current_player.say_uno()

            # Check for winner
            winner = self.check_winner()
            if winner:
                self.game_state = GameState.ROUND_OVER
                return False

            # Move to next player
            self.next_turn()

            return True

        except ValueError as e:
            if "Not enough cards to reshuffle" in str(
                e
            ) or "Deck is empty and reshuffling is disabled" in str(e):
                self._end_game_with_scores()
                return False
            else:
                # Re-raise other errors
                raise e

    def _end_game_with_scores(self) -> None:
        """
        End the game by calculating scores and determining winner based on hand scores
        """
        self.game_state = GameState.ROUND_OVER

        # Calculate hand scores for all players
        hand_scores = {}
        for player in self.players:
            score = player.calculate_hand_score()
            hand_scores[player.player_id] = score

        # Find player with lowest score (winner)
        min_score = min(hand_scores.values())
        winners = [
            player
            for player in self.players
            if hand_scores[player.player_id] == min_score
        ]

        if len(winners) == 1:
            winner = winners[0]
        else:
            # Tie - choose the one with fewer cards
            min_hand_size = min(winner.get_hand_size() for winner in winners)
            final_winners = [
                winner for winner in winners if winner.get_hand_size() == min_hand_size
            ]

            if len(final_winners) == 1:
                winner = final_winners[0]
            else:
                # Still tied - choose randomly
                winner = random.choice(final_winners)

    def auto_play_game(self) -> Player:
        """
        Automatically play the game until there's a winner or deadlock
        """
        if not self.auto_play:
            raise ValueError("Auto-play is disabled")

        self.initialize_game()

        # Main game loop
        while self.game_state == GameState.IN_PROGRESS:
            try:
                if not self.play_turn():
                    break
            except ValueError as e:
                if "Not enough cards to reshuffle" in str(
                    e
                ) or "Deck is empty and reshuffling is disabled" in str(e):
                    self._end_game_with_scores()
                    break
                else:
                    raise e

        # Determine and return winner
        if self.game_state == GameState.ROUND_OVER:
            # Find the actual winner (player with no cards or lowest score)
            winner = self.check_winner()
            if not winner:
                # If no one has empty hand, calculate based on scores
                hand_scores = {
                    player.player_id: player.calculate_hand_score()
                    for player in self.players
                }
                min_score = min(hand_scores.values())
                winners = [
                    player
                    for player in self.players
                    if hand_scores[player.player_id] == min_score
                ]
                winner = winners[0] if winners else None

            if winner:
                return winner

        return None

    def get_game_status(self) -> Dict:
        """
        Get current game status
        """
        return {
            "game_state": self.game_state.value,
            "current_player": self.get_current_player().name,
            "current_player_id": self.get_current_player().player_id,
            "top_card": str(self.get_top_discard_card()),
            "current_color": self.current_color.name if self.current_color else None,
            "game_direction": self.game_direction.value,
            "deck_size": self.deck.size(),
            "discard_pile_size": len(self.discard_pile),
            "turn_count": self.turn_count,
            "players": [
                {
                    "name": player.name,
                    "player_id": player.player_id,
                    "hand_size": player.get_hand_size(),
                    "has_uno": player.has_uno(),
                    "score": self.scores[player.player_id],
                }
                for player in self.players
            ],
        }
