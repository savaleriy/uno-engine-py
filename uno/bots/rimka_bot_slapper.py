from __future__ import annotations

from typing import List, Optional

from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class ZemtsevBot(Player):
    """
    A bot that plays its wild cards first.
    """

    AUTHOR = "Zemtsev Dmitriy"

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
                index, card = wilds[0]
                new_color = self.choose_color(card) if card.is_wild else None
                return self.play_card(card, new_color)
            else:
                R = []  # 0
                B = []  # 1
                G = []  # 2
                Y = []  # 3
                for i in self.hand:
                    if i.color.name == "RED":
                        R.append(i)
                    elif i.color.name == "BLUE":
                        B.append(i)
                    elif i.color.name == "GREEN":
                        G.append(i)
                    elif i.color.name == "YELLOW":
                        Y.append(i)
                crds = [[R, len(R)], [B, len(B)], [G, len(G)], [Y, len(Y)]]
                mx = 0
                maj = []
                for i in crds:
                    if i[1] > mx:
                        mx = i[1]
                        maj = i[0]
                mx = 0
                final_card = Card
                for i in maj:
                    if i.label.value > mx:
                        final_card = i
                return self.play_card(final_card)
        else:
            # No playable cards, must draw
            return PlayerAction(draw_card=True)

    def choose_color(self, wild_card: Card) -> CardColor:
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
