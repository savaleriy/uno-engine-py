from __future__ import annotations

import random
from random import getrandbits
from typing import List, Optional

from ..engine.card import Card, CardColor
from ..player.player import Player, PlayerAction


class fluxbot(Player):
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
        playable_indices = [
        i for i, card in enumerate(self.hand) 
        if card.can_play_on(self._top_card, self._current_color)
    ]
    
        if not playable_indices:
            return PlayerAction(draw_card=True)
    
        selected_index = random.choice(playable_indices)
        card_to_play = self.hand[selected_index]
        new_color = None
    
        if card_to_play.is_wild:
            new_color = self.choose_color(card_to_play)
            
        return self.play_card(card_to_play, new_color)
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
