import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from modules.game_state import GameState

def test_estado_inicial():
    gs = GameState()
    assert gs.fase == "inicio"

def test_transicion_fase_juego():
    gs = GameState()
    gs.establecer_fase("fase_juego")
    assert gs.fase == "fase_juego"
