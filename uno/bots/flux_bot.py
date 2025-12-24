from __future__ import annotations

import random
from typing import List, Optional

from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class fluxbot(Player):

    def __init__(self, name: str, player_id: int):
        super().__init__(name, player_id)
        self._top_card: Optional[Card] = None
        self._current_color: Optional[CardColor] = None
        self._playable_indices_cache: List[int] = []

    def update_game_state(
        self, playable_cards: List[Card], top_card: Card, current_color: CardColor
    ) -> None:
        self._top_card = top_card
        self._current_color = current_color
        # Кэшируем индексы играбельных карт для быстрого доступа
        self._playable_indices_cache = [
            i for i, card in enumerate(self.hand) 
            if card.can_play_on(top_card, current_color)
        ]

    def choose_action(self) -> PlayerAction:
        # Используем кэшированные индексы
        if not self._playable_indices_cache:
            return PlayerAction(draw_card=True)
    
        # Предпочитаем специальные карты (скип, реверс, +2), если доступны
        special_indices = [
            i for i in self._playable_indices_cache
            if self.hand[i].is_skip or self.hand[i].is_reverse or self.hand[i].is_draw_two
        ]
        
        # Если есть специальные карты, играем их с большей вероятностью (70%)
        if special_indices and random.random() < 0.7:
            selected_index = random.choice(special_indices)
        else:
            selected_index = random.choice(self._playable_indices_cache)
            
        card_to_play = self.hand[selected_index]
        new_color = None
    
        if card_to_play.is_wild:
            new_color = self.choose_color()
            
        return self.play_card(card_to_play, new_color)

    def choose_color(self) -> CardColor:
        # Создаем список допустимых цветов (исключая черный/дикий)
        valid_colors = [
            CardColor.RED,
            CardColor.BLUE, 
            CardColor.GREEN,
            CardColor.YELLOW,
        ]
        
        # Подсчитываем карты каждого цвета в руке
        color_counts = {}
        for color in valid_colors:
            color_counts[color] = 0
        
        for card in self.hand:
            if card.color in valid_colors:  # Только не дикие карты
                color_counts[card.color] += 1
        
        # Находим максимальное количество карт одного цвета
        max_count = 0
        best_color = None
        
        for color, count in color_counts.items():
            if count > max_count:
                max_count = count
                best_color = color
        
        # Если все счетчики 0 или best_color не определен, выбираем случайный
        if best_color is None or max_count == 0:
            return random.choice(valid_colors)
            
        return best_color

    def decide_say_uno(self) -> bool:
        # Всегда говорить UNO, чтобы избежать штрафа
        return True

    def should_play_drawn_card(self, drawn_card: Card) -> bool:
        # Проверяем, можно ли сыграть взятую карту
        return drawn_card.can_play_on(self._top_card, self._current_color)