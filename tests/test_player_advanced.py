# tests/test_player_advanced.py
import pytest
import pygame
import math
from unittest.mock import Mock, patch
from game.player import Player


class TestPlayerInitialization:
    """Tests pour l'initialisation du joueur."""
    
    @pytest.mark.unit
    def test_player_init_with_mocks(self, mock_pygame_sound, mock_pygame_image):
        """Test l'initialisation du joueur avec des mocks."""
        player = Player(x=100, y=200)
        
        assert player.rect.centerx == 100
        assert player.rect.centery == 200
        assert player.hp == player.max_hp
        assert player.level == 1
        assert player.xp == 0
        assert player.speed > 0
        assert player.attack_range > 0
        assert player.attack_damage > 0
    
    @pytest.mark.unit
    def test_player_initial_stats(self, sample_player):
        """Test les statistiques initiales du joueur."""
        assert sample_player.hp == sample_player.max_hp
        assert sample_player.level == 1
        assert sample_player.xp == 0
        assert sample_player.speed == 150
        assert sample_player.attack_range == 150
        assert sample_player.attack_damage == 3
        assert sample_player.regen_rate == 0.2
    
    @pytest.mark.unit
    def test_player_initial_timers(self, sample_player):
        """Test que tous les timers sont correctement initialisés."""
        assert sample_player.attack_timer >= 0
        assert sample_player.dash_timer == 0
        assert sample_player.scream_timer == 0
        assert sample_player.dash_time_left == 0
        assert not sample_player.attacking
        assert not sample_player.show_scream_cone


class TestPlayerMovement:
    """Tests pour le système de mouvement du joueur."""
    
    @pytest.mark.unit
    def test_movement_single_direction(self, sample_player, dummy_keys):
        """Test le mouvement dans une seule direction."""
        dummy_keys[pygame.K_d] = True  # droite
        initial_x = sample_player.rect.x
        
        sample_player.update(dummy_keys, dt=1.0)
        
        assert sample_player.rect.x > initial_x
        assert sample_player.direction == 'right'
    
    @pytest.mark.unit
    def test_movement_diagonal_normalized(self, sample_player, dummy_keys):
        """Test que le mouvement diagonal est normalisé."""
        dummy_keys[pygame.K_d] = True  # droite
        dummy_keys[pygame.K_z] = True  # haut
        
        initial_pos = (sample_player.rect.x, sample_player.rect.y)
        sample_player.update(dummy_keys, dt=1.0)
        
        # Calculer la distance parcourue
        dx = sample_player.rect.x - initial_pos[0]
        dy = sample_player.rect.y - initial_pos[1]
        distance = math.hypot(dx, dy)
        
        # La distance devrait être environ égale à speed * dt
        expected_distance = sample_player.speed * 1.0
        assert abs(distance - expected_distance) < 1.0  # tolerance
    
    @pytest.mark.unit
    def test_movement_boundary_clamping(self, sample_player, dummy_keys):
        """Test que le joueur reste dans les limites de la carte."""
        from game.settings import MAP_WIDTH, MAP_HEIGHT
        
        # Placer le joueur près du bord
        sample_player.rect.x = MAP_WIDTH - 10
        sample_player.rect.y = MAP_HEIGHT - 10
        
        # Essayer de bouger au-delà des limites
        dummy_keys[pygame.K_d] = True  # droite
        dummy_keys[pygame.K_s] = True  # bas
        
        sample_player.update(dummy_keys, dt=10.0)  # grand dt
        
        assert sample_player.rect.x <= MAP_WIDTH - sample_player.rect.width
        assert sample_player.rect.y <= MAP_HEIGHT - sample_player.rect.height
    
    @pytest.mark.unit
    def test_animation_updates_on_movement(self, sample_player, dummy_keys):
        """Test que l'animation se met à jour pendant le mouvement."""
        dummy_keys[pygame.K_d] = True
        
        initial_anim_timer = sample_player.anim_timer
        sample_player.update(dummy_keys, dt=0.5)
        
        assert sample_player.anim_timer > initial_anim_timer


class TestPlayerCombat:
    """Tests pour le système de combat du joueur."""
    
    @pytest.mark.unit
    def test_attack_cooldown_management(self, sample_player):
        """Test la gestion du cooldown d'attaque."""
        # Attaque initiale
        assert sample_player.can_attack()
        
        sample_player.attack([], (0, 0))
        assert not sample_player.can_attack()
        
        # Après le cooldown
        sample_player.update({}, dt=sample_player.attack_cooldown + 0.1)
        assert sample_player.can_attack()
    
    @pytest.mark.unit
    def test_attack_hits_enemy_in_range_and_angle(self, sample_player):
        """Test qu'une attaque touche un ennemi dans la portée et l'angle."""
        # Créer un ennemi factice
        enemy = Mock()
        enemy.rect = pygame.Rect(0, 0, 20, 20)
        enemy.rect.center = (sample_player.rect.centerx + 50, sample_player.rect.centery)
        enemy.hp = 100
        enemy.take_damage = Mock()
        
        # Attaquer vers l'ennemi
        mouse_pos = enemy.rect.center
        sample_player.attack([enemy], mouse_pos)
        
        enemy.take_damage.assert_called_once_with(sample_player.attack_damage)
    
    @pytest.mark.unit
    def test_attack_misses_enemy_out_of_range(self, sample_player):
        """Test qu'une attaque rate un ennemi hors de portée."""
        enemy = Mock()
        enemy.rect = pygame.Rect(0, 0, 20, 20)
        enemy.rect.center = (sample_player.rect.centerx + sample_player.attack_range + 100, 
                           sample_player.rect.centery)
        enemy.hp = 100
        enemy.take_damage = Mock()
        
        sample_player.attack([enemy], enemy.rect.center)
        
        enemy.take_damage.assert_not_called()
    
    @pytest.mark.unit
    def test_attack_cone_angle_limitation(self, sample_player):
        """Test que l'attaque respecte les limites d'angle du cône."""
        # Ennemi derrière le joueur
        enemy = Mock()
        enemy.rect = pygame.Rect(0, 0, 20, 20)
        enemy.rect.center = (sample_player.rect.centerx - 50, sample_player.rect.centery)
        enemy.hp = 100
        enemy.take_damage = Mock()
        
        # Attaquer vers l'avant
        mouse_pos = (sample_player.rect.centerx + 100, sample_player.rect.centery)
        sample_player.attack([enemy], mouse_pos)
        
        enemy.take_damage.assert_not_called()


class TestPlayerProgression:
    """Tests pour le système de progression du joueur."""
    
    @pytest.mark.unit
    def test_gain_xp_simple(self, sample_player):
        """Test le gain d'XP simple."""
        initial_xp = sample_player.xp
        sample_player.gain_xp(50)
        
        assert sample_player.xp == initial_xp + 50
    
    @pytest.mark.unit
    def test_level_up_on_xp_threshold(self, sample_player):
        """Test le passage de niveau au seuil d'XP."""
        initial_level = sample_player.level
        sample_player.gain_xp(sample_player.next_level_xp)
        
        assert sample_player.level == initial_level + 1
        assert sample_player.new_level
    
    @pytest.mark.unit
    def test_level_up_overflow_xp(self, sample_player):
        """Test que l'XP en trop est conservé après un niveau."""
        overflow = 25
        total_xp = sample_player.next_level_xp + overflow
        
        sample_player.gain_xp(total_xp)
        
        assert sample_player.level == 2
        assert sample_player.xp == overflow
    
    @pytest.mark.unit
    def test_multiple_level_ups(self, sample_player):
        """Test les niveaux multiples en une fois."""
        # XP pour 3 niveaux
        massive_xp = sample_player.next_level_xp * 3
        initial_level = sample_player.level
        
        sample_player.gain_xp(massive_xp)
        
        assert sample_player.level > initial_level + 2
    
    @pytest.mark.unit
    def test_xp_bonus_application(self, sample_player):
        """Test l'application des bonus d'XP."""
        sample_player.xp_bonus = 0.5  # 50% bonus
        base_xp = 100
        
        sample_player.gain_xp(base_xp)
        
        expected_xp = int(base_xp * 1.5)
        assert sample_player.xp == expected_xp


class TestPlayerUpgrades:
    """Tests pour le système d'améliorations du joueur."""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("upgrade_key,expected_effect", [
        ("Strength Boost", lambda p: p.attack_damage),
        ("Vitality Surge", lambda p: p.max_hp),
        ("Haste", lambda p: p.speed),
        ("Extended Reach", lambda p: p.attack_range),
    ])
    def test_upgrade_effects(self, sample_player, upgrade_key, expected_effect):
        """Test les effets des différentes améliorations."""
        before = expected_effect(sample_player)
        sample_player.apply_upgrade(upgrade_key)
        after = expected_effect(sample_player)
        
        assert after > before
    
    @pytest.mark.unit
    def test_quick_reflexes_upgrade(self, sample_player):
        """Test spécifique pour Quick Reflexes (multiplicateur)."""
        before = sample_player.attack_cooldown
        sample_player.apply_upgrade("Quick Reflexes")
        after = sample_player.attack_cooldown
        
        assert after < before
        assert after == pytest.approx(before * 0.85)
    
    @pytest.mark.unit
    def test_vitality_surge_heals_player(self, sample_player):
        """Test que Vitality Surge soigne le joueur."""
        sample_player.hp = 50  # Blessé
        before_hp = sample_player.hp
        
        sample_player.apply_upgrade("Vitality Surge")
        
        assert sample_player.hp > before_hp


class TestPlayerSpecialAbilities:
    """Tests pour les capacités spéciales du joueur."""
    
    @pytest.mark.unit
    def test_dash_activation(self, sample_player, dummy_keys):
        """Test l'activation du dash."""
        dummy_keys[pygame.K_d] = True      # direction
        dummy_keys[pygame.K_SPACE] = True  # dash
        
        sample_player.update(dummy_keys, dt=0.1)
        
        assert sample_player.dash_time_left > 0
        assert sample_player.dash_timer > 0
    
    @pytest.mark.unit
    def test_dash_movement_speed(self, sample_player, dummy_keys):
        """Test que le dash augmente la vitesse de déplacement."""
        dummy_keys[pygame.K_d] = True
        dummy_keys[pygame.K_SPACE] = True
        
        initial_x = sample_player.rect.x
        sample_player.update(dummy_keys, dt=0.1)
        
        # En dash, la vitesse devrait être beaucoup plus grande
        distance = sample_player.rect.x - initial_x
        expected_distance = sample_player.dash_speed * 0.1
        
        assert abs(distance - expected_distance) < 10  # tolérance
    
    @pytest.mark.unit
    def test_dash_cooldown_prevents_consecutive_dashes(self, sample_player, dummy_keys):
        """Test que le cooldown empêche les dashs consécutifs."""
        dummy_keys[pygame.K_d] = True
        dummy_keys[pygame.K_SPACE] = True
        
        # Premier dash
        sample_player.update(dummy_keys, dt=0.1)
        first_dash_timer = sample_player.dash_timer
        
        # Attendre que le dash se termine
        sample_player.update({}, dt=sample_player.dash_duration + 0.1)
        
        # Essayer un deuxième dash immédiatement
        sample_player.update(dummy_keys, dt=0.1)
        
        # Le cooldown devrait empêcher le deuxième dash
        assert sample_player.dash_time_left == 0
    
    @pytest.mark.unit
    def test_scream_ability(self, sample_player):
        """Test de la capacité de cri."""
        assert sample_player.scream_timer == 0
        
        sample_player.scream([], [], (100, 100))
        
        assert sample_player.scream_timer > 0
        assert sample_player.show_scream_cone
    
    @pytest.mark.unit
    def test_scream_damages_enemies_in_cone(self, sample_player):
        """Test que le cri inflige des dégâts aux ennemis dans le cône."""
        enemy = Mock()
        enemy.rect = pygame.Rect(0, 0, 20, 20)
        enemy.rect.center = (sample_player.rect.centerx + 50, sample_player.rect.centery)
        enemy.hp = 100
        enemy.slow_timer = 0
        
        # Cri vers l'ennemi
        mouse_pos = enemy.rect.center
        sample_player.scream([enemy], [], mouse_pos)
        
        assert enemy.hp < 100
        assert enemy.slow_timer > 0


class TestPlayerBonuses:
    """Tests pour les bonus temporaires du joueur."""
    
    @pytest.mark.unit
    def test_magnet_bonus_activation(self, sample_player):
        """Test l'activation du bonus aimant."""
        assert not sample_player.magnet_active
        
        sample_player.apply_bonus("magnet")
        
        assert sample_player.magnet_active
        assert sample_player.magnet_timer > 0
    
    @pytest.mark.unit
    def test_magnet_bonus_expires(self, sample_player):
        """Test que le bonus aimant expire."""
        sample_player.apply_bonus("magnet")
        
        # Faire passer le temps
        sample_player.update({}, dt=sample_player.magnet_duration + 1)
        
        assert not sample_player.magnet_active
        assert sample_player.magnet_timer == 0


class TestPlayerHealthSystem:
    """Tests pour le système de santé du joueur."""
    
    @pytest.mark.unit
    def test_take_damage(self, sample_player):
        """Test les dégâts subis par le joueur."""
        initial_hp = sample_player.hp
        damage = 25
        
        sample_player.take_damage(damage)
        
        assert sample_player.hp == initial_hp - damage
    
    @pytest.mark.unit
    def test_take_damage_cannot_go_below_zero(self, sample_player):
        """Test que les HP ne peuvent pas descendre sous zéro."""
        sample_player.take_damage(sample_player.hp + 100)
        
        assert sample_player.hp == 0
    
    @pytest.mark.unit
    def test_regeneration(self, sample_player):
        """Test la régénération passive."""
        sample_player.hp = 50  # Blessé
        initial_hp = sample_player.hp
        
        sample_player.update({}, dt=1.0)
        
        expected_hp = min(initial_hp + sample_player.regen_rate * 1.0, sample_player.max_hp)
        assert sample_player.hp == pytest.approx(expected_hp)
    
    @pytest.mark.unit
    def test_regeneration_doesnt_exceed_max(self, sample_player):
        """Test que la régénération ne dépasse pas le max HP."""
        sample_player.hp = sample_player.max_hp - 1
        
        sample_player.update({}, dt=100.0)  # Long temps
        
        assert sample_player.hp == sample_player.max_hp


@pytest.mark.integration
class TestPlayerIntegration:
    """Tests d'intégration pour le joueur."""
    
    def test_full_combat_cycle(self, sample_player):
        """Test d'un cycle de combat complet."""
        enemy = Mock()
        enemy.rect = pygame.Rect(0, 0, 20, 20)
        enemy.rect.center = (sample_player.rect.centerx + 50, sample_player.rect.centery)
        enemy.hp = 10
        enemy.take_damage = Mock()
        
        # Attaque
        sample_player.attack([enemy], enemy.rect.center)
        enemy.take_damage.assert_called_once()
        
        # Attendre le cooldown
        sample_player.update({}, dt=sample_player.attack_cooldown)
        
        # Deuxième attaque possible
        assert sample_player.can_attack()
    
    def test_level_progression_with_upgrades(self, sample_player):
        """Test de progression de niveau avec améliorations."""
        initial_stats = {
            'damage': sample_player.attack_damage,
            'hp': sample_player.max_hp,
            'speed': sample_player.speed
        }
        
        # Gagner de l'XP et passer de niveau
        sample_player.gain_xp(sample_player.next_level_xp)
        
        # Appliquer une amélioration
        sample_player.apply_upgrade("Strength Boost")
        
        assert sample_player.level == 2
        assert sample_player.attack_damage > initial_stats['damage'] 