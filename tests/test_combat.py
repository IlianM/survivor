import pygame
import pytest
from game.player import Player

class DummyEnemy:
    """Un ennemi factice avec take_damage() et flash_timer."""
    def __init__(self, dx, dy):
        self.rect = pygame.Rect(0, 0, 10, 10)
        self.rect.center = (dx, dy)
        self.hp = 10
        self.flash_timer = 0
        self.flash_duration = 0.5
    def take_damage(self, amount):
        self.hp -= amount
        self.flash_timer = self.flash_duration

@pytest.fixture
def melee_player():
    p = Player(x=100, y=100)
    # on s'assure qu'on peut attaquer immédiatement
    p.attack_timer = p.attack_cooldown
    return p

def test_can_attack_initial(melee_player):
    assert melee_player.can_attack()

def test_attack_starts_cooldown_and_visual(melee_player):
    melee_player.attack_timer = melee_player.attack_cooldown
    melee_player.attacking = False
    melee_player.attack([], (0, 0))
    # après un appel, on passe en cooldown et on déclenche le slash visuel
    assert melee_player.attacking is True
    assert melee_player.attack_timer == 0
    assert melee_player.attack_timer_visual == melee_player.attack_duration

def test_attack_hits_enemy_in_range(melee_player):
    # place l'ennemi juste à portée, devant le joueur
    ex = melee_player.rect.centerx + melee_player.attack_range - 1
    ey = melee_player.rect.centery
    enemy = DummyEnemy(ex, ey)
    melee_player.attack([enemy], (ex, ey))
    # il perd ses PV et flash_timer est réglé
    assert enemy.hp == 10 - melee_player.attack_damage
    assert enemy.flash_timer == pytest.approx(enemy.flash_duration)

def test_attack_misses_enemy_out_of_range(melee_player):
    # place l'ennemi juste hors portée
    ex = melee_player.rect.centerx + melee_player.attack_range + 10
    ey = melee_player.rect.centery
    enemy = DummyEnemy(ex, ey)
    melee_player.attack([enemy], (ex, ey))
    assert enemy.hp == 10  # pas de dégâts

def test_attack_misses_enemy_outside_angle(melee_player):
    # place l'ennemi derrière le joueur (angle > 90°)
    ex = melee_player.rect.centerx - (melee_player.attack_range - 1)
    ey = melee_player.rect.centery
    enemy = DummyEnemy(ex, ey)
    # on attaque vers la droite
    melee_player.attack([enemy], (melee_player.rect.centerx + 1, melee_player.rect.centery))
    assert enemy.hp == 10  # pas de dégâts
