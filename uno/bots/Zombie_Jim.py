from __future__ import annotations

from random import choice
from typing import List, Optional

from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class Zombie_JimBot(Player):
    """
    This bot will eat your brains.
    """

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
        valid_selections = []
        for index, card in enumerate(self.hand):
            if card.can_play_on(self._top_card, self._current_color):
                valid_selections.append((index, card))

        if valid_selections:
            # print(valid_selections)

            wilds = [
                selection for selection in valid_selections if selection[1].is_wild
            ]
            # print(valid_selections)
            wilds2 = [selection for selection in valid_selections if not selection[1].is_wild]
            # print(wilds)
            if wilds:
                def wild_priority(selection):
                    card = selection[1]
                    if hasattr(card, 'value'):
                        if card.value == 'WILD_DRAW_FOUR':
                            return 0
                        elif card.value == 'DRAW_TWO':
                            return 1
                        elif card.value == 'SKIP':
                            return 2
                        elif card.value == 'REVERSE':
                            return 3
                    return 4
                wilds_sorted = sorted(wilds, key=wild_priority)
                index, card = wilds_sorted[0]
                new_color = self.choose_color(card) if card.is_wild else None
                return self.play_card(card, new_color)
            elif wilds2:
                ipi = []
                for i, card in valid_selections:
                    ipi.append(card)
                card = ipi[-1]
                return self.play_card(card)
            else:
                return self.play_card(card)
        else:
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

        for card in self.hand:
            if not card.is_wild:  
                color_counts[card.color] += 1

        return max(color_counts, key=color_counts.get)

    def decide_say_uno(self) -> bool:
        return True

    def should_play_drawn_card(self, drawn_card: Card) -> bool:
        return drawn_card.can_play_on(self._top_card, self._current_color)

# else:
            #     def card_priority(card: Card) -> int:
            #         return -sum(1 for c in self.hand if c.color == card.color)

            #     ipi = [card for _, card in valid_selections]
            #     selected_card = min(ipi, key=card_priority)
            #     return self.play_card(selected_card)