# tests/test_upgrades.py

import pytest
from game.player import Player

@pytest.fixture
def player():
    # On crée un joueur "nu" pour ces tests
    p = Player(x=0, y=0)
    # On neutralise l’XP et la santé pour ne pas interférer
    p.xp = 0
    p.level = 1
    p.next_level_xp = 100
    p.hp = p.max_hp = 50
    return p

def test_apply_upgrade_strength_boost(player):
    base = player.attack_damage
    player.apply_upgrade("Strength Boost")
    assert player.attack_damage == base + 3

def test_apply_upgrade_vitality_surge(player):
    base_max = player.max_hp
    base_hp  = player.hp
    player.apply_upgrade("Vitality Surge")
    assert player.max_hp == base_max + 5
    assert player.hp      == base_hp  + 5

def test_apply_upgrade_quick_reflexes(player):
    base_cd = player.attack_cooldown
    player.apply_upgrade("Quick Reflexes")
    assert player.attack_cooldown == pytest.approx(base_cd * 0.85)

def test_apply_upgrade_haste(player):
    base_spd = player.speed
    player.apply_upgrade("Haste")
    assert player.speed == base_spd + 30

def test_apply_upgrade_extended_reach(player):
    base_rng = player.attack_range
    player.apply_upgrade("Extended Reach")
    assert player.attack_range == base_rng + 30

def test_apply_upgrade_xp_bonus_and_gain(player):
    # On teste l’upgrade
    assert player.xp_bonus == 0.0
    player.apply_upgrade("XP Bonus")
    assert player.xp_bonus == pytest.approx(0.25)

    # Puis l’effet sur gain_xp (palier à 100)
    player.xp = 0
    player.level = 1
    player.next_level_xp = 100
    player.gain_xp(100)
    # Level up une fois, le surplus (100*0.25 = 25) reste
    assert player.level == 2
    assert player.xp == 25
