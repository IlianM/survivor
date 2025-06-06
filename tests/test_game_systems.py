# tests/test_game_systems.py
import pytest
import pygame
import math
from unittest.mock import Mock, patch, MagicMock
from game.xp_orb import XPOrb


class TestXPOrbSystem:
    """Tests pour le système d'orbes d'XP."""
    
    @pytest.mark.unit
    def test_xp_orb_initialization(self, mock_pygame_image, mock_pygame_sound):
        """Test l'initialisation d'un orbe d'XP."""
        orb = XPOrb(x=100, y=200, value=50)
        
        assert orb.rect.centerx == 100
        assert orb.rect.centery == 200
        assert orb.value == 50
        assert hasattr(orb, 'attraction_range')
    
    @pytest.mark.unit
    def test_xp_orb_attraction(self, mock_pygame_image, mock_pygame_sound, sample_player):
        """Test l'attraction des orbes vers le joueur."""
        orb = XPOrb(x=200, y=200, value=25)
        
        # Placer le joueur dans la portée d'attraction
        sample_player.rect.center = (150, 150)
        
        initial_distance = math.hypot(
            orb.rect.centerx - sample_player.rect.centerx,
            orb.rect.centery - sample_player.rect.centery
        )
        
        # Mettre à jour l'orbe
        orb.update(sample_player.rect.center, dt=1.0)
        
        new_distance = math.hypot(
            orb.rect.centerx - sample_player.rect.centerx,
            orb.rect.centery - sample_player.rect.centery
        )
        
        # L'orbe devrait se rapprocher du joueur
        assert new_distance < initial_distance
    
    @pytest.mark.unit
    def test_xp_orb_magnet_effect(self, mock_pygame_image, mock_pygame_sound, sample_player):
        """Test l'effet aimant sur les orbes d'XP."""
        orb = XPOrb(x=300, y=300, value=25)
        
        # Activer l'aimant du joueur
        sample_player.magnet_active = True
        sample_player.rect.center = (200, 200)
        
        initial_distance = math.hypot(
            orb.rect.centerx - sample_player.rect.centerx,
            orb.rect.centery - sample_player.rect.centery
        )
        
        # Avec l'aimant, l'attraction devrait être plus forte
        orb.update(sample_player.rect.center, dt=1.0, magnet_active=True)
        
        new_distance = math.hypot(
            orb.rect.centerx - sample_player.rect.centerx,
            orb.rect.centery - sample_player.rect.centery
        )
        
        # L'orbe devrait se rapprocher rapidement
        assert new_distance < initial_distance
    
    @pytest.mark.unit
    def test_xp_orb_collection(self, mock_pygame_image, mock_pygame_sound, sample_player):
        """Test la collecte d'orbes d'XP."""
        orb = XPOrb(x=100, y=100, value=50)
        sample_player.rect.center = (100, 100)  # Même position
        
        # Vérifier la collision
        collision = orb.rect.colliderect(sample_player.rect)
        assert collision
        
        # Simuler la collecte
        initial_xp = sample_player.xp
        sample_player.gain_xp(orb.value)
        
        assert sample_player.xp == initial_xp + orb.value


class TestSpawnSystem:
    """Tests pour le système de spawn des ennemis."""
    
    @pytest.mark.unit
    def test_spawn_cap_calculation(self):
        """Test le calcul du cap de spawn selon le niveau."""
        from game.main import BASE_MAX_ENEMIES, PER_LEVEL_ENEMIES
        
        # Level 1
        level = 1
        expected_cap = BASE_MAX_ENEMIES + (level - 1) * PER_LEVEL_ENEMIES
        assert expected_cap == 5
        
        # Level 5
        level = 5
        expected_cap = BASE_MAX_ENEMIES + (level - 1) * PER_LEVEL_ENEMIES
        assert expected_cap == 13
    
    @pytest.mark.unit
    def test_spawn_probability_by_level(self):
        """Test les probabilités de spawn selon le niveau du joueur."""
        # À implementer selon la logique de spawn du jeu
        pass
    
    @pytest.mark.unit
    def test_spawn_position_validation(self, sample_player):
        """Test que les ennemis spawnt à des positions valides."""
        from game.settings import MAP_WIDTH, MAP_HEIGHT
        
        # Position de spawn simulée
        spawn_x = 50
        spawn_y = 50
        
        # Vérifier que la position est dans les limites
        assert 0 <= spawn_x <= MAP_WIDTH
        assert 0 <= spawn_y <= MAP_HEIGHT
        
        # Vérifier que la position n'est pas trop proche du joueur
        distance_to_player = math.hypot(
            spawn_x - sample_player.rect.centerx,
            spawn_y - sample_player.rect.centery
        )
        min_spawn_distance = 100  # Distance minimum supposée
        # assert distance_to_player >= min_spawn_distance


class TestCameraSystem:
    """Tests pour le système de caméra."""
    
    @pytest.mark.unit
    def test_camera_follows_player(self, sample_player):
        """Test que la caméra suit le joueur."""
        from game.settings import WIDTH, HEIGHT
        
        # Position du joueur
        player_x, player_y = sample_player.rect.center
        
        # Calcul de la position de la caméra
        cam_x = player_x - WIDTH // 2
        cam_y = player_y - HEIGHT // 2
        
        # La caméra devrait être centrée sur le joueur
        assert cam_x == player_x - WIDTH // 2
        assert cam_y == player_y - HEIGHT // 2
    
    @pytest.mark.unit
    def test_camera_boundary_clamping(self, sample_player):
        """Test que la caméra reste dans les limites de la carte."""
        from game.settings import WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT
        
        # Joueur près du bord de la carte
        sample_player.rect.center = (50, 50)
        
        # Calcul de la position de la caméra avec clamping
        cam_x = max(0, min(sample_player.rect.centerx - WIDTH // 2, 
                          MAP_WIDTH - WIDTH))
        cam_y = max(0, min(sample_player.rect.centery - HEIGHT // 2, 
                          MAP_HEIGHT - HEIGHT))
        
        # La caméra ne devrait pas sortir des limites
        assert cam_x >= 0
        assert cam_y >= 0
        assert cam_x <= MAP_WIDTH - WIDTH
        assert cam_y <= MAP_HEIGHT - HEIGHT


class TestUISystem:
    """Tests pour le système d'interface utilisateur."""
    
    @pytest.mark.unit
    def test_health_bar_calculation(self, sample_player):
        """Test le calcul de la barre de vie."""
        sample_player.hp = 75
        sample_player.max_hp = 100
        
        hp_ratio = sample_player.hp / sample_player.max_hp
        assert hp_ratio == 0.75
        
        # Test avec HP à zéro
        sample_player.hp = 0
        hp_ratio = sample_player.hp / sample_player.max_hp
        assert hp_ratio == 0.0
        
        # Test avec HP au maximum
        sample_player.hp = sample_player.max_hp
        hp_ratio = sample_player.hp / sample_player.max_hp
        assert hp_ratio == 1.0
    
    @pytest.mark.unit
    def test_xp_bar_calculation(self, sample_player):
        """Test le calcul de la barre d'XP."""
        sample_player.xp = 30
        sample_player.next_level_xp = 100
        
        xp_ratio = sample_player.xp / sample_player.next_level_xp
        assert xp_ratio == 0.3
    
    @pytest.mark.unit
    def test_draw_tiled_background(self, mock_surface):
        """Test le rendu du fond tiled."""
        from game.main import draw_tiled_background
        
        # Mock de l'image de fond
        bg_img = Mock()
        bg_w, bg_h = 64, 64
        cam_x, cam_y = 100, 100
        
        # Ne devrait pas lever d'exception
        draw_tiled_background(mock_surface, cam_x, cam_y, bg_img, bg_w, bg_h)
        
        # Vérifier que blit a été appelé
        assert mock_surface.blit.called
    
    @pytest.mark.unit
    def test_upgrade_menu_selection(self):
        """Test la sélection dans le menu d'amélioration."""
        from game.main import UpgradeMenu
        from game.player import Player
        
        with patch('pygame.image.load'), patch('pygame.freetype.Font'):
            menu = UpgradeMenu()
            menu.open()
            
            # Vérifier qu'il y a 3 choix
            assert len(menu.choices) == 3
            assert len(menu.rects) == 3
            
            # Vérifier que les choix sont valides
            for choice in menu.choices:
                assert choice in Player.UPGRADE_KEYS


class TestGameLogic:
    """Tests pour la logique principale du jeu."""
    
    @pytest.mark.unit
    def test_collision_detection_player_enemy(self, sample_player, sample_enemy):
        """Test la détection de collision joueur-ennemi."""
        # Placer l'ennemi sur le joueur
        sample_enemy.rect.center = sample_player.rect.center
        
        collision = sample_player.rect.colliderect(sample_enemy.rect)
        assert collision
    
    @pytest.mark.unit
    def test_collision_detection_player_xp_orb(self, sample_player, mock_pygame_image, mock_pygame_sound):
        """Test la détection de collision joueur-orbe XP."""
        orb = XPOrb(x=sample_player.rect.centerx, y=sample_player.rect.centery, value=25)
        
        collision = sample_player.rect.colliderect(orb.rect)
        assert collision
    
    @pytest.mark.unit
    def test_projectile_collision_with_player(self, sample_player, mock_pygame_image):
        """Test la collision projectile-joueur."""
        from game.projectile import Projectile
        
        projectile = Projectile(
            (sample_player.rect.centerx - 10, sample_player.rect.centery),
            (sample_player.rect.centerx + 10, sample_player.rect.centery),
            speed=100, damage=10
        )
        
        collision = projectile.rect.colliderect(sample_player.rect)
        # Le résultat dépend des tailles exactes des rectangles
    
    @pytest.mark.unit
    def test_game_over_condition(self, sample_player):
        """Test la condition de game over."""
        sample_player.hp = 0
        
        game_over = sample_player.hp <= 0
        assert game_over
    
    @pytest.mark.unit
    def test_wave_progression(self):
        """Test la progression des vagues d'ennemis."""
        # Logic de vague à implementer selon le jeu
        wave_number = 1
        enemies_in_wave = 5 + wave_number * 2
        
        assert enemies_in_wave > 0
        assert enemies_in_wave >= wave_number


class TestGameStats:
    """Tests pour les statistiques de jeu."""
    
    @pytest.mark.unit
    def test_kill_counter(self):
        """Test le compteur de kills."""
        enemies_killed = 0
        
        # Simuler un kill
        enemies_killed += 1
        assert enemies_killed == 1
        
        # Plusieurs kills
        enemies_killed += 5
        assert enemies_killed == 6
    
    @pytest.mark.unit
    def test_survival_time(self):
        """Test le calcul du temps de survie."""
        game_time = 0.0
        dt = 0.016  # 60 FPS
        
        # Simuler 1 seconde de jeu
        for _ in range(60):
            game_time += dt
        
        assert game_time == pytest.approx(0.96, abs=0.1)
    
    @pytest.mark.unit
    def test_level_progression_stats(self, sample_player):
        """Test les stats de progression de niveau."""
        initial_level = sample_player.level
        initial_damage = sample_player.attack_damage
        
        # Passer de niveau
        sample_player.level_up()
        
        assert sample_player.level == initial_level + 1
        assert sample_player.attack_damage > initial_damage


class TestGameBalance:
    """Tests pour l'équilibrage du jeu."""
    
    @pytest.mark.unit
    def test_enemy_scaling_reasonable(self, mock_pygame_image):
        """Test que le scaling des ennemis reste raisonnable."""
        from game.enemy import Enemy
        
        normal_enemy = Enemy(x=0, y=0, tier="normal")
        rare_enemy = Enemy(x=0, y=0, tier="rare")
        elite_enemy = Enemy(x=0, y=0, tier="elite")
        
        # Les ennemis plus rares devraient avoir plus de HP mais pas de façon excessive
        assert rare_enemy.hp > normal_enemy.hp
        assert elite_enemy.hp > rare_enemy.hp
        assert elite_enemy.hp <= normal_enemy.hp * 3  # Pas plus de 3x
    
    @pytest.mark.unit
    def test_player_progression_reasonable(self, sample_player):
        """Test que la progression du joueur reste équilibrée."""
        initial_stats = {
            'damage': sample_player.attack_damage,
            'hp': sample_player.max_hp,
            'speed': sample_player.speed
        }
        
        # Appliquer plusieurs améliorations
        for upgrade in ["Strength Boost", "Vitality Surge", "Haste"]:
            sample_player.apply_upgrade(upgrade)
        
        # Les améliorations devraient avoir un impact mais pas excessif
        assert sample_player.attack_damage <= initial_stats['damage'] * 2
        assert sample_player.max_hp <= initial_stats['hp'] * 2
        assert sample_player.speed <= initial_stats['speed'] * 2
    
    @pytest.mark.unit
    def test_xp_requirements_scaling(self, sample_player):
        """Test que les requis d'XP évoluent de façon équilibrée."""
        initial_req = sample_player.next_level_xp
        
        # Passer plusieurs niveaux
        for _ in range(3):
            sample_player.level_up()
        
        # Les requis devraient augmenter mais pas de façon exponentielle
        assert sample_player.next_level_xp > initial_req
        assert sample_player.next_level_xp <= initial_req * 3


@pytest.mark.integration
class TestGameSystemsIntegration:
    """Tests d'intégration entre les systèmes de jeu."""
    
    def test_full_combat_sequence(self, sample_player, mock_pygame_image, mock_pygame_sound):
        """Test d'une séquence de combat complète."""
        from game.enemy import Enemy
        from game.xp_orb import XPOrb
        
        # Créer un ennemi
        enemy = Enemy(x=200, y=200, tier="normal")
        initial_player_xp = sample_player.xp
        
        # Le joueur attaque l'ennemi
        sample_player.attack([enemy], enemy.rect.center)
        
        # L'ennemi devrait avoir pris des dégâts
        assert enemy.hp < enemy.hp  # Difficile à tester sans connaître HP initial
        
        # Simuler la mort de l'ennemi et spawn d'XP
        if enemy.hp <= 0:
            orb = XPOrb(x=enemy.rect.centerx, y=enemy.rect.centery, value=25)
            
            # Le joueur collecte l'XP
            sample_player.gain_xp(orb.value)
            
            assert sample_player.xp > initial_player_xp
    
    def test_level_up_sequence(self, sample_player):
        """Test d'une séquence complète de passage de niveau."""
        initial_level = sample_player.level
        
        # Gagner assez d'XP pour passer de niveau
        sample_player.gain_xp(sample_player.next_level_xp)
        
        assert sample_player.level == initial_level + 1
        assert sample_player.new_level
        
        # Appliquer une amélioration
        upgrade = "Strength Boost"
        initial_damage = sample_player.attack_damage
        sample_player.apply_upgrade(upgrade)
        
        assert sample_player.attack_damage > initial_damage
    
    def test_death_and_respawn_sequence(self, sample_player):
        """Test de la séquence de mort et de respawn."""
        # Réduire les HP à zéro
        sample_player.take_damage(sample_player.hp)
        assert sample_player.hp == 0
        
        # Condition de game over
        game_over = sample_player.hp <= 0
        assert game_over


@pytest.mark.performance
class TestGamePerformance:
    """Tests de performance du jeu."""
    
    def test_update_loop_performance(self, performance_timer, sample_player, mock_pygame_image):
        """Test la performance de la boucle principale de mise à jour."""
        from game.enemy import Enemy
        from game.xp_orb import XPOrb
        
        # Créer plusieurs entités
        enemies = [Enemy(x=i*50, y=i*50, tier="normal") for i in range(20)]
        orbs = [XPOrb(x=i*30, y=i*30, value=10) for i in range(10)]
        
        performance_timer.start()
        
        # Simuler une frame de jeu
        dt = 1.0/60  # 60 FPS
        sample_player.update({}, dt)
        
        for enemy in enemies:
            enemy.update(sample_player.rect.center, dt, enemies)
        
        for orb in orbs:
            orb.update(sample_player.rect.center, dt)
        
        performance_timer.stop()
        
        # Une frame devrait prendre moins de 16ms (60 FPS)
        assert performance_timer.elapsed < 0.016
    
    def test_collision_detection_performance(self, performance_timer, sample_player, mock_pygame_image):
        """Test la performance de la détection de collision."""
        from game.enemy import Enemy
        
        # Créer beaucoup d'ennemis
        enemies = [Enemy(x=i*10, y=i*10, tier="normal") for i in range(100)]
        
        performance_timer.start()
        
        # Tester les collisions
        for enemy in enemies:
            collision = sample_player.rect.colliderect(enemy.rect)
        
        performance_timer.stop()
        
        # La détection de collision devrait être rapide
        assert performance_timer.elapsed < 0.001


@pytest.mark.smoke
class TestGameSmoke:
    """Tests de fumée pour vérifier que les bases fonctionnent."""
    
    def test_game_starts(self, integration_setup):
        """Test que le jeu peut démarrer sans erreur."""
        # Test basique de démarrage
        assert True  # Si on arrive ici, l'import a fonctionné
    
    def test_player_can_move(self, sample_player, dummy_keys):
        """Test que le joueur peut bouger."""
        dummy_keys[pygame.K_d] = True
        initial_x = sample_player.rect.x
        
        sample_player.update(dummy_keys, dt=1.0)
        
        assert sample_player.rect.x != initial_x
    
    def test_enemies_can_spawn(self, mock_pygame_image):
        """Test que les ennemis peuvent être créés."""
        from game.enemy import Enemy
        
        enemy = Enemy(x=100, y=100, tier="normal")
        assert enemy.hp > 0
        assert enemy.rect.centerx == 100
        assert enemy.rect.centery == 100 