import math
import pytest
import pygame

from game.player import Player
from game.enemy import Enemy

@pytest.fixture
def player():
    p = Player(x=100, y=100)
    # remettre dash et scream prêts à déclencher
    p.dash_timer = 0
    p.dash_time_left = 0
    p.scream_timer = 0
    p.show_scream_cone = False
    return p

# --- 4. Cri (scream) ---

def test_scream_damage_and_slow(player):
    """Un mob dans le cône perd hp et reçoit slow_timer."""
    # place un ennemi juste devant le joueur (dans le cône)
    e = Enemy(x=player.rect.centerx, 
              y=player.rect.centery - int(player.scream_range/2),
              speed=0, tier='normal', player_level=1)
    hp0 = e.hp

    # on crie droit vers le haut
    mouse_pos = (player.rect.centerx, player.rect.centery - 1)
    player.scream([e], [], mouse_pos)

    assert e.hp == hp0 - player.scream_damage
    assert pytest.approx(e.slow_timer, rel=1e-6) == player.scream_slow_duration

def test_scream_cone_disappears(player):
    """Le cône de scream disparaît après scream_cone_duration."""
    player.scream([], [], (0,0))
    assert player.show_scream_cone

    # on fait passer le temps
    player.update({}, dt=player.scream_cone_duration + 0.1)
    assert not player.show_scream_cone

def test_scream_cooldown(player):
    """Le scream_timer décrémente puis n’est plus positif quand le cooldown est écoulé."""
    player.scream([], [], (0,0))
    t0 = player.scream_timer
    assert pytest.approx(t0) == player.scream_cooldown

    # décrément partiel
    player.update({}, dt=1.0)
    assert pytest.approx(player.scream_timer) == t0 - 1.0

    # décrémente jusqu’à zéro (peut devenir négatif)
    player.update({}, dt=player.scream_timer + 1.0)
    assert player.scream_timer <= 0