# tests/test_player.py
import pytest
import pygame
from game.player import Player

@pytest.fixture
def player():
    # instancie un joueur au niveau 1, avec 0 XP
    p = Player(x=0, y=0)
    p.level = 1
    p.xp = 0
    p.next_level_xp = 100
    p.hp = p.max_hp = 50
    # on reset les timers
    p.dash_timer = 0
    p.dash_time_left = 0
    p.scream_timer = 0
    p.show_scream_cone = False
    return p

def test_gain_xp_level_up(player):
    player.gain_xp(100)
    assert player.level == 2
    assert player.xp == 0
    assert player.next_level_xp > 100

def test_gain_xp_overflow(player):
    player.gain_xp(150)
    assert player.level == 2
    assert player.xp == 50

def test_take_damage_and_clamp(player):
    player.take_damage(10)
    assert player.hp == 40
    player.take_damage(1000)
    assert player.hp == 0

def test_regen_ne_pas_depasser_max(player):
    player.hp = 10
    player.update({}, dt=1.0)
    assert pytest.approx(player.hp, rel=1e-3) == 10 + player.regen_rate * 1.0
    player.hp = player.max_hp - 1
    player.update({}, dt=500)
    assert player.hp <= player.max_hp

def test_dash_sets_timers_and_duration(player):
    # dash sans cooldown ni durée initiale
    keys = {
        pygame.K_z: True,
        pygame.K_d: True,
        pygame.K_SPACE: True
    }
    player.update(keys, dt=0)  # déclenche le dash
    assert player.dash_timer == pytest.approx(player.dash_cooldown)
    assert player.dash_time_left == pytest.approx(player.dash_duration)

def test_dash_cooldown_prevents_dash(player):
    # on simule un dash déjà en cooldown
    player.dash_timer = player.dash_cooldown * 0.5
    player.dash_time_left = 0
    keys = {pygame.K_z: True, pygame.K_SPACE: True}
    player.update(keys, dt=0)
    # pas de nouveau dash lancé
    assert player.dash_time_left == 0
    # le cooldown continue de se décrémenter
    prev_cd = player.dash_timer
    player.update({}, dt=0.1)
    assert player.dash_timer < prev_cd

def test_scream_sets_and_expires_cone(player):
    # au départ, scream dispo
    assert player.scream_timer == 0
    assert not player.show_scream_cone

    # on crie
    player.scream([], [], (0, 0))
    assert player.scream_timer == pytest.approx(player.scream_cooldown)
    assert player.show_scream_cone is True
    # la durée du cône est dans l'attribut scream_cone_duration
    assert player.scream_cone_timer == pytest.approx(player.scream_cone_duration)

    # après la durée du cône, il disparaît
    player.update({}, dt=player.scream_cone_duration + 1e-3)
    assert player.show_scream_cone is False
    assert player.scream_cone_timer <= 0

    # le cooldown du scream persiste tant qu'on ne l'attend pas
    prev = player.scream_timer
    player.update({}, dt=0.1)
    assert player.scream_timer < prev
    player.update({}, dt=player.scream_cooldown)
    assert player.scream_timer == pytest.approx(0, abs=1e-3)
