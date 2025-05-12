import math
import pytest
import pygame

from game.player import Player


@pytest.fixture
def player():
    p = Player(x=100, y=100)
    # remettre dash et scream prêts à déclencher
    p.dash_timer = 0
    p.dash_time_left = 0
    p.scream_timer = 0
    p.show_scream_cone = False
    return p

# --- 3. Dash ---

@pytest.mark.parametrize("key, expected_dir", [
    (pygame.K_z, (0, -1)),   # up
    (pygame.K_s, (0,  1)),   # down
    (pygame.K_q, (-1, 0)),   # left
    (pygame.K_d, ( 1, 0)),   # right
])
def test_dash_direction_cardinal(player, key, expected_dir):
    """Lorsque l’on appuie sur SPACE+direction, dash_dir doit être le vecteur cardinal correct
    et dash_time_left == dash_duration."""
    # prépare l’état
    player.dash_timer = 0
    player.dash_time_left = 0

    # simule la frappe
    keys = { key: True, pygame.K_SPACE: True }
    player.update(keys, dt=0.01)

    assert player.dash_dir == expected_dir
    assert pytest.approx(player.dash_time_left, rel=1e-6) == player.dash_duration

def test_dash_cooldown_block(player):
    """Tenter un dash alors que dash_timer > 0 ne déclenche rien."""
    player.dash_timer = 1.0       # reste du cooldown
    player.dash_time_left = 0

    keys = { pygame.K_z: True, pygame.K_SPACE: True }
    player.update(keys, dt=0.1)

    # pas de dash déclenché
    assert player.dash_time_left == 0

def test_dash_moves_player(player):
    """Quand dash_time_left > 0, update déplace le joueur de dash_speed*dt."""
    # forcé un dash vers le bas
    player.dash_time_left = player.dash_duration
    player.dash_dir = (0, 1)

    x0, y0 = player.rect.x, player.rect.y
    player.update({}, dt=1.0)

    # doit avoir avancé de dash_speed pixels
    assert pytest.approx(player.rect.x, abs=1e-6) == x0
    assert pytest.approx(player.rect.y, abs=1e-6) == y0 + player.dash_speed
