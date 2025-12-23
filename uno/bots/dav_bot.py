from __future__ import annotations

from typing import List, Optional

from ..engine.card import Card, CardColor, CardLabel
from ..player.player import Player, PlayerAction


class SkripkinBot(Player):
    AUTHOR = "Mikhail Skripkin"

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
            (i, card)
            for i, card in enumerate(self.hand)
            if card.can_play_on(self._top_card, self._current_color)
        ]

        if not valid_selections:
            return PlayerAction(draw_card=True)

        draw_cards = [
            sel
            for sel in valid_selections
            if sel[1].label in (CardLabel.DRAW_TWO, CardLabel.WILD_DRAW_FOUR)
        ]
        if draw_cards:
            card = draw_cards[0][1]
            new_color = self.choose_color(card) if card.is_wild else None
            return self.play_card(card, new_color)

        action_cards = [
            sel
            for sel in valid_selections
            if sel[1].label in (CardLabel.SKIP, CardLabel.REVERSE)
        ]
        if action_cards:
            card = action_cards[0][1]
            new_color = self.choose_color(card) if card.is_wild else None
            return self.play_card(card, new_color)

        wilds = [
            sel
            for sel in valid_selections
            if sel[1].is_wild and sel[1].label != CardLabel.WILD_DRAW_FOUR
        ]
        if wilds:
            card = wilds[0][1]
            new_color = self.choose_color(card)
            return self.play_card(card, new_color)

        number_cards = [
            sel
            for sel in valid_selections
            if not sel[1].is_wild
            and sel[1].label
            not in (CardLabel.DRAW_TWO, CardLabel.SKIP, CardLabel.REVERSE)
        ]
        if number_cards:
            try:
                number_cards.sort(key=lambda x: x[1].value)
                return self.play_card(number_cards[0][1])
            except (AttributeError, ValueError):
                pass

        wilds = [sel for sel in valid_selections if sel[1].is_wild]
        if wilds:
            card = wilds[0][1]
            new_color = self.choose_color(card) if card.is_wild else None
            return self.play_card(card, new_color)

        color_groups = {
            color: []
            for color in (
                CardColor.RED,
                CardColor.BLUE,
                CardColor.GREEN,
                CardColor.YELLOW,
            )
        }
        for card in self.hand:
            if card.color in color_groups:
                color_groups[card.color].append(card)

        dominant_color = max(color_groups, key=lambda c: len(color_groups[c]))
        dominant_cards = color_groups[dominant_color]

        if dominant_cards:
            best_card = max(dominant_cards, key=lambda c: c.label.value)
            return self.play_card(best_card)

        return self.play_card(valid_selections[0][1])

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
