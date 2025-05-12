import pytest
from game.enemy import Enemy
from game.goblin_mage import GoblinMage
from game.boss import Boss

def test_enemy_hp_by_tier():
    """Vérifie que les PV augmentent du tier 'normal' → 'rare' → 'elite'."""
    e_normal = Enemy(0, 0, speed=10, tier='normal', player_level=1)
    e_rare   = Enemy(0, 0, speed=10, tier='rare',   player_level=1)
    e_elite  = Enemy(0, 0, speed=10, tier='elite',  player_level=1)
    assert e_normal.max_hp < e_rare.max_hp < e_elite.max_hp

def test_goblin_mage_init():
    """Le GoblinMage doit avoir des PV, dégâts et la liste de projectiles."""
    gm = GoblinMage(50, 50)
    assert hasattr(gm, 'projectiles')
    assert gm.max_hp > 0
    assert gm.damage > 0

def test_boss_init_stats():
    """
    Le Boss hérite des PV d'un elite×5, gagne xp player_level*10,
    et a un damage ≥1 ainsi qu'un attack_cooldown raisonnable.
    """
    ref_elite = Enemy(0, 0, speed=40, tier='elite', player_level=5)
    b = Boss(0, 0, player_level=5)
    assert b.max_hp == ref_elite.max_hp * 5
    assert b.hp == b.max_hp
    assert b.xp_value == 5 * 10
    assert b.damage >= 1
    assert b.attack_cooldown >= 1.0

def test_boss_attack_range():
    """La portée d'attaque du boss doit être la moitié de la taille du sprite."""
    b = Boss(0, 0, player_level=5)
    expected = max(b.rect.width, b.rect.height) * 0.5
    assert b.attack_range == expected
