import pytest
import pygame
import math
from game.player import Player

@pytest.fixture
def player():
    # initialise pygame en mode headless
    pygame.init()
    pygame.display.set_mode((1, 1))
    p = Player(x=0, y=0)
    p.speed = 100
    # on replace le joueur à (0,0) pour plus de simplicité
    p.rect = pygame.Rect(0, 0, 32, 32)
    return p

def test_move_cardinal_up(player):
    """Se déplacer tout droit vers le haut diminue y de speed*dt."""
    # place the player away from the top/left edge so clamp doesn’t cancel movement
    player.rect.x, player.rect.y = 200, 200
    initial_x, initial_y = player.rect.x, player.rect.y
    keys = {pygame.K_z: True}
    player.update(keys, dt=1.0)
    assert player.rect.x == initial_x
    assert player.rect.y == initial_y - player.speed

def test_move_cardinal_right(player):
    """Se déplacer tout droit vers la droite augmente x de speed*dt."""
    initial_x, initial_y = player.rect.x, player.rect.y
    keys = {pygame.K_d: True}
    player.update(keys, dt=1.0)
    assert player.rect.x == initial_x + player.speed
    assert player.rect.y == initial_y

def test_move_diagonal_normalized(player):
    """
    Se déplacer en diagonale doit être normalisé :
    distance parcourue == speed * dt, pas speed*√2.
    """
    # same here – start well inside the map
    player.rect.x, player.rect.y = 200, 200
    initial_x, initial_y = player.rect.x, player.rect.y
    keys = {pygame.K_z: True, pygame.K_d: True}
    player.update(keys, dt=1.0)
    dx = player.rect.x - initial_x
    dy = player.rect.y - initial_y
    dist = math.hypot(dx, dy)
    assert pytest.approx(dist, rel=1e-2) == player.speed
