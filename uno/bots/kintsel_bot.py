from __future__ import annotations
from typing import List, Optional

from ..engine.card import Card, CardColor, CardLabel
from ..player.player import Player, PlayerAction

# БИБИБИБЛИОТЕКААА!!! ^^^^^^^^^^^


class KintselBot(Player):  # <<<<<<<< НАШ КЛАССИКК
    AUTHOR = "Nikita Kintsel"

    def __init__(self, name: str, player_id: int):
        super().__init__(name, player_id)
        self._top_card: Optional[Card] = None
        self._current_color: Optional[CardColor] = None

    def update_game_state(
        self, playable_cards: List[Card], topcard: Card, currentcolor: CardColor
    ) -> None:
        self._topcard = topcard
        self._current_color = currentcolor

    def choose_action(self) -> PlayerAction:  # тутс реализована основная тактикаа игрыы
        valid_selections = []
        for index, card in enumerate(self.hand):
            if card.can_play_on(self._topcard, self._current_color):
                valid_selections.append((index, card))
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
                card = number_cards[0][1]
                return self.play_card(card)
            except (AttributeError, ValueError):
                pass
        if valid_selections:
            wilds = [
                selection for selection in valid_selections if selection[1].is_wild
            ]

            if wilds:
                index, card = wilds[0]
                new_color = self.choose_color(card) if card.is_wild else None
                return self.play_card(card, new_color)
            else:
                color_groups = {
                    CardColor.RED: [],
                    CardColor.BLUE: [],
                    CardColor.GREEN: [],
                    CardColor.YELLOW: [],
                }
                for card in self.hand:
                    if card.color in color_groups:
                        color_groups[card.color].append(card)
                dominant_color = max(
                    color_groups.keys(), key=lambda color: len(color_groups[color])
                )
                dominant_cards = color_groups[dominant_color]
                best_card = max(dominant_cards, key=lambda card: card.label.value)
            return self.play_card(best_card)
        else:
            return PlayerAction(draw_card=True)

    def choose_color(self, wildcard: Card) -> CardColor:  # тутсс мы выбираемм цвеет!
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

    def decide_say_uno(self) -> bool:  # туттсс мы говоримм унооо!
        return True

    def should_play_drawn_card(
        self, drawncard: Card
    ) -> bool:  # проверочкаа можно ли сыграть новой картоойй!
        return drawncard.can_play_on(self._topcard, self._current_color)


# <3
