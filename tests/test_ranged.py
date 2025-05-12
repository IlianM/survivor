import math
import pygame
import pytest
from game.goblin_mage import GoblinMage
from game.projectile   import Fireball
from game.player       import Player

@pytest.fixture
def dummy_player():
    # un joueur au centre
    p = Player(x=200, y=200)
    return p

def test_fireball_initialization(dummy_player):
    # le Fireball part de (0,0) vers le joueur
    fb = Fireball(0, 0, dummy_player.rect.center)
    assert isinstance(fb, Fireball)

def test_fireball_moves_towards_target(dummy_player):
    fb = Fireball(0, 0, dummy_player.rect.center)
    x0, y0 = fb.rect.center
    fb.update(dt=1.0)
    x1, y1 = fb.rect.center
    # il doit avancer dans la bonne direction
    dx0 = dummy_player.rect.centerx - x0
    dy0 = dummy_player.rect.centery  - y0
    dx1 = x1 - x0
    dy1 = y1 - y0
    # même signe
    assert dx0 * dx1 > 0 or dy0 * dy1 > 0

def test_fireball_offscreen():
    fb = Fireball(0,0,(0,0))
    # on place le projectile hors de l'écran
    fb.rect.x = -fb.rect.width - 1
    assert fb.off_screen()

def test_goblin_mage_fires_when_on_screen(dummy_player):
    gm = GoblinMage(x=dummy_player.rect.centerx, y=dummy_player.rect.centery)
    gm.fire_timer = 0.0
    gm.projectiles.clear()
    # cam_x, cam_y à (0,0) font que le mage est "on screen"
    gm.update(dummy_player, dt=0.0, cam_x=0, cam_y=0)
    assert len(gm.projectiles) == 1
    assert isinstance(gm.projectiles[0], Fireball)

def test_goblin_mage_respects_cooldown(dummy_player):
    gm = GoblinMage(x=dummy_player.rect.centerx, y=dummy_player.rect.centery)
    gm.fire_timer = gm.fire_cooldown  # encore en cooldown
    before = list(gm.projectiles)
    gm.update(dummy_player, dt=1.0, cam_x=0, cam_y=0)
    # aucune nouvelle flamme tant que fire_timer > 0
    assert gm.projectiles == before
