# tests/test_scream_input.py
import pygame
import pytest

from game.main import handle_scream_input
from game.player import Player

@pytest.fixture(autouse=True)
def init_pygame():
    # dummy display pour convert_alpha() et get_pos()
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()

def test_handle_scream_input_key_c(monkeypatch):
    player = Player(0, 0)
    enemy_list = []
    mages = []
    called = False

    # on remplace player.scream par un stub
    def fake_scream(e_list, m_list, pos):
        nonlocal called
        called = True
    monkeypatch.setattr(player, "scream", fake_scream)

    # on simule un event KEYDOWN C
    ev = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_c})
    monkeypatch.setattr(pygame.event, "get", lambda: [ev])

    # on positionne la souris quelque part
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (10, 20))

    # appel de la fonction
    res = handle_scream_input(ev, player, enemy_list, mages, cam_x=5, cam_y=7)

    assert res is True
    assert called is True

def test_handle_scream_input_other(monkeypatch):
    player = Player(0, 0)
    enemy_list = []
    mages = []
    called = False
    monkeypatch.setattr(player, "scream", lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not be called")))

    # un event qui n'est ni C ni clic droit
    ev = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_x})
    res = handle_scream_input(ev, player, enemy_list, mages, cam_x=0, cam_y=0)
    assert res is False
