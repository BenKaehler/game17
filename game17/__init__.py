from .game_runners import (
        replay, single, round_robin, battle_royale, vs_zombies)
from .basic_mover import get_mover_factory

__version__ = "1.0"


__all__ = ['replay', 'single', 'round_robin', 'battle_royale', 'vs_zombies',
           'get_mover_factory']
