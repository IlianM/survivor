import pytest
import pygame
from game.goblin_mage import GoblinMage
from game.projectile import Fireball
from game.player import Player

@pytest.fixture
def player():
    # joueur basique pour les tests de GoblinMage
    p = Player(x=0, y=0)
    return p

def test_goblin_mage_init():
    """Le GoblinMage doit être initialisé avec des PV, dégâts et une liste vide de projectiles."""
    gm = GoblinMage(50, 50)
    assert hasattr(gm, 'projectiles')
    assert isinstance(gm.projectiles, list) and gm.projectiles == []
    assert gm.max_hp > 0 and gm.hp == gm.max_hp
    assert hasattr(gm, 'damage') and gm.damage > 0

def test_goblin_mage_fire_cooldown(player):
    """
    Après un update, le mage tire une boule de feu si fire_timer <= 0 ;
    il ne doit pas tirer à nouveau tant que fire_timer > 0,
    puis peut tirer de nouveau une fois cooldown écoulé.
    """
    # Positionner mage et joueur au même endroit pour garantir on_screen
    gm = GoblinMage(player.rect.centerx, player.rect.centery)
    gm.fire_timer = 0.0

    # 1) Premier update → tir
    gm.update(player, dt=0.1, cam_x=gm.rect.x, cam_y=gm.rect.y)
    assert len(gm.projectiles) == 1

    # 2) update immédiat → pas de tir (cooldown)
    gm.update(player, dt=0.1, cam_x=gm.rect.x, cam_y=gm.rect.y)
    assert len(gm.projectiles) == 1

    # 3) simuler expiration du cooldown
    gm.fire_timer = 0.0
    gm.update(player, dt=0, cam_x=gm.rect.x, cam_y=gm.rect.y)
    assert len(gm.projectiles) == 2

def test_fireball_off_screen_removal(player, monkeypatch):
    """
    Si un Fireball.off_screen() devient True, il doit être retiré de gm.projectiles.
    """
    gm = GoblinMage(player.rect.centerx, player.rect.centery)
    # Empêcher tout nouveau tir
    gm.fire_timer = gm.fire_cooldown

    # Créer une fireball et forcer off_screen → True
    fb = Fireball(gm.rect.centerx, gm.rect.centery, player.rect.center)
    monkeypatch.setattr(fb, 'off_screen', lambda: True)

    gm.projectiles = [fb]
    gm.update(player, dt=0.1, cam_x=gm.rect.x, cam_y=gm.rect.y)
    assert fb not in gm.projectiles
