from __future__ import annotations

from random import *
from typing import List, Optional

from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class DavBot(Player):

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
        playable = [
            card for card in self.hand
            if card.can_play_on(self._top_card, self._current_color)
        ]

        if playable:
            special_cards = [c for c in playable if c.is_wild]
            regular_cards = [c for c in playable if not c.is_wild]

            if special_cards and choice([True] * 7 + [False] * 3):
                card_to_play = choice(special_cards)
            else:
                card_to_play = choice(regular_cards) if regular_cards else choice(special_cards)

            new_color = None
            if card_to_play.is_wild:
                new_color = self.choose_color(card_to_play)

            return self.play_card(card_to_play, new_color)

        return PlayerAction(draw_card=True)

    def choose_color(self, wild_card: Card) -> CardColor:
        color_count = {CardColor.RED: 0, CardColor.BLUE: 0, CardColor.GREEN: 0, CardColor.YELLOW: 0}

        for card in self.hand:
            if card.color in color_count:
                color_count[card.color] += 1

        best_color = CardColor.RED
        max_count = 0
        for color, count in color_count.items():
            if count > max_count:
                max_count = count
                best_color = color

        if max_count == 0:
            return random.choice([CardColor.RED, CardColor.BLUE, CardColor.GREEN, CardColor.YELLOW])

        return best_color

    def decide_say_uno(self) -> bool:
        return True


    def should_play_drawn_card(self, drawn_card: Card) -> bool:
        return True
