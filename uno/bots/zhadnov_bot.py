from __future__ import annotations

from typing import List, Optional

from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class ZhadnovBot(Player):
    AUTHOR = "Ivan Zhadnov"
    """
    A bot that plays its wild cards first.
    """

    def __init__(self, name: str, player_id: int):
        super().__init__(name, player_id)
        self._top_card: Optional[Card] = None
        self._current_color: Optional[CardColor] = None

    def update_game_state(
        self, playable_cards: List[Card], top_card: Card, current_color: CardColor
    ) -> None:
        """
        Update bot's knowledge of current game state
        """
        self._top_card = top_card
        self._current_color = current_color

    def choose_action(self) -> PlayerAction:
        """
        Returns a valid card or draw action. Favors wild cards first.
        """
        # Create a list of valid selections with (index, card) tuples
        valid_selections = []

        for index, card in enumerate(self.hand):
            if card.can_play_on(self._top_card, self._current_color):
                valid_selections.append((index, card))

        if valid_selections:
            # Find wild cards first
            wilds = [
                selection for selection in valid_selections if selection[1].is_wild
            ]

            if wilds:
                # Play the first wild card found
                index, card = wilds[0]
                new_color = self.choose_color(card) if card.is_wild else None
                return self.play_card(card, new_color)
            else:
                red = []
                blue = []
                green = []
                yellow = []
                for clrs in self.hand:
                    if clrs.color.name == "RED":
                        red.append(clrs)
                    elif clrs.color.name == "BLUE":
                        blue.append(clrs)
                    elif clrs.color.name == "GREEN":
                        green.append(clrs)
                    elif clrs.color.name == "YELLOW":
                        yellow.append(clrs)
                cards = [
                    [red, len(red)],
                    [blue, len(blue)],
                    [green, len(green)],
                    [yellow, len(yellow)],
                ]
                max_count = 0
                max_list = []
                for i in cards:
                    if i[1] > max_count:
                        max_count = i[1]
                        max_list = i[0]
                max_count = 0
                max_count_card = Card
                for i in max_list:
                    if i.label.value > max_count:
                        max_count_card = i
                return self.play_card(max_count_card)
        else:
            return PlayerAction(draw_card=True)

    def choose_color(self, wild_card: Card) -> CardColor:
        """
        Returns an advantageous color for a wild card.
        """
        color_counts = {
            color: 0
            for color in [
                CardColor.RED,
                CardColor.BLUE,
                CardColor.GREEN,
                CardColor.YELLOW,
            ]
        }

        # Count non-wild cards by color
        for card in self.hand:
            if not card.is_wild:  # card.color != CardColor.WILD
                color_counts[card.color] += 1

        # Return the color with the most cards
        return max(color_counts, key=color_counts.get)

    def decide_say_uno(self) -> bool:
        return True

    def should_play_drawn_card(self, drawn_card: Card) -> bool:
        return drawn_card.can_play_on(self._top_card, self._current_color)

