from __future__ import annotations
import random

from typing import List, Optional

from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class AkimVBot(Player):
    AUTHOR = "Akim Volgin"

    def __init__(self, name: str, player_id: int):
        super().__init__(name, player_id)
        self._top_card: Optional[Card] = None
        self._current_color: Optional[CardColor] = None

    def update_game_state(
        self, playable_cards: List[Card], top_card: Card, current_color: CardColor
    ) -> None:
        self._top_card = top_card
        self._current_color = current_color

    def choose_action(self) -> PlayerAction:
        valid_selections = [
            card
            for card in self.hand
            if card.can_play_on(self._top_card, self._current_color)
        ]

        if not valid_selections:
            return PlayerAction(draw_card=True)
        color_counts = {
            color: 0
            for color in [
                CardColor.RED,
                CardColor.BLUE,
                CardColor.GREEN,
                CardColor.YELLOW,
            ]
        }
        for card in self.hand:
            if card.color in color_counts:
                color_counts[card.color] += 1
        max_color = max(color_counts, key=color_counts.get)
        selection = None

        for card in valid_selections:
            if card.label.REVERSE:
                selection = card
        if selection is None:
            for card in valid_selections:
                if card.label.SKIP:
                    selection = card
                if card.label.DRAW_TWO:
                    selection = card
                if card.label.WILD_DRAW_FOUR:
                    selection = card
        if selection is None:
            num_card = [card for card in valid_selections if 0 <= card.label <= 9]
            if num_card:
                x_color = [x for x in num_card if x.color == max_color]
                if x_color:
                    selection = max(x_color)

        return PlayerAction(selection, draw_card=False)

    def choose_color(self, wild_card: Card) -> CardColor:
        return random.choice(
            [CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW]
        )

    def decide_say_uno(self) -> bool:
        """
        Randomly decide whether to say UNO (50% chance)
        """
        return True

    def should_play_drawn_card(self, drawn_card: Card) -> bool:
        if drawn_card.can_play_on(self._top_card, self._current_color):
            return True
        return True
