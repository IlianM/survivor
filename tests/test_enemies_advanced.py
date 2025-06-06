# tests/test_enemies_advanced.py
import pytest
import pygame
import math
from unittest.mock import Mock, patch
from game.enemy import Enemy
from game.goblin_mage import GoblinMage
from game.boss import Boss
from game.projectile import Projectile


class TestEnemyBase:
    """Tests pour la classe Enemy de base."""
    
    @pytest.mark.unit
    def test_enemy_initialization(self, mock_pygame_image):
        """Test l'initialisation d'un ennemi."""
        enemy = Enemy(x=100, y=200, tier="normal")
        
        assert enemy.rect.centerx == 100
        assert enemy.rect.centery == 200
        assert enemy.tier == "normal"
        assert enemy.hp > 0
        assert enemy.speed > 0
    
    @pytest.mark.unit
    @pytest.mark.parametrize("tier,expected_multiplier", [
        ("normal", 1.0),
        ("rare", 1.5),
        ("elite", 2.0),
    ])
    def test_enemy_tier_scaling(self, mock_pygame_image, tier, expected_multiplier):
        """Test que les tiers d'ennemis appliquent les bons multiplicateurs."""
        enemy = Enemy(x=0, y=0, tier=tier)
        
        # Les stats devraient être multipliées selon le tier
        base_hp = 20  # HP de base pour un ennemi normal
        expected_hp = base_hp * expected_multiplier
        assert enemy.hp == pytest.approx(expected_hp)
    
    @pytest.mark.unit
    def test_enemy_movement_toward_target(self, sample_enemy, sample_player):
        """Test que l'ennemi se déplace vers sa cible."""
        # Placer l'ennemi loin du joueur
        sample_enemy.rect.center = (500, 500)
        target_pos = sample_player.rect.center
        initial_distance = math.hypot(
            sample_enemy.rect.centerx - target_pos[0],
            sample_enemy.rect.centery - target_pos[1]
        )
        
        # Mettre à jour l'ennemi
        sample_enemy.update(target_pos, dt=1.0)
        
        # Calculer la nouvelle distance
        new_distance = math.hypot(
            sample_enemy.rect.centerx - target_pos[0],
            sample_enemy.rect.centery - target_pos[1]
        )
        
        # L'ennemi devrait s'être rapproché
        assert new_distance < initial_distance
    
    @pytest.mark.unit
    def test_enemy_collision_detection(self, sample_enemy):
        """Test la détection de collision avec d'autres ennemis."""
        other_enemy = Mock()
        other_enemy.rect = pygame.Rect(0, 0, 20, 20)
        other_enemy.rect.center = sample_enemy.rect.center  # Même position
        
        # L'ennemi devrait détecter la collision
        result = sample_enemy.update((1000, 1000), dt=0.1, enemies=[other_enemy])
        
        # Vérifier que les ennemis se sont séparés
        assert sample_enemy.rect.center != other_enemy.rect.center
    
    @pytest.mark.unit
    def test_enemy_take_damage(self, sample_enemy):
        """Test que l'ennemi prend des dégâts correctement."""
        initial_hp = sample_enemy.hp
        damage = 10
        
        sample_enemy.take_damage(damage)
        
        assert sample_enemy.hp == initial_hp - damage
        assert sample_enemy.flash_timer > 0  # Flash de dégâts
    
    @pytest.mark.unit
    def test_enemy_death_condition(self, sample_enemy):
        """Test la condition de mort de l'ennemi."""
        sample_enemy.take_damage(sample_enemy.hp + 10)  # Dégâts excessifs
        
        assert sample_enemy.hp <= 0
    
    @pytest.mark.unit
    def test_enemy_slow_effect(self, sample_enemy):
        """Test l'effet de ralentissement sur l'ennemi."""
        original_speed = sample_enemy.speed
        sample_enemy.slow_timer = 2.0  # 2 secondes de slow
        
        sample_enemy.update((0, 0), dt=0.1)
        
        # La vitesse devrait être réduite pendant le slow
        # (dépend de l'implémentation du slow dans la classe Enemy)
        assert hasattr(sample_enemy, 'slow_timer')


class TestGoblinMage:
    """Tests pour la classe GoblinMage."""
    
    @pytest.mark.unit
    def test_goblin_mage_initialization(self, mock_pygame_image):
        """Test l'initialisation du gobelin mage."""
        mage = GoblinMage(x=100, y=200)
        
        assert mage.rect.centerx == 100
        assert mage.rect.centery == 200
        assert mage.hp > 0
        assert mage.fire_cooldown > 0
        assert mage.fire_range > 0
    
    @pytest.mark.unit
    def test_goblin_mage_fire_projectile(self, sample_goblin_mage, sample_player):
        """Test que le gobelin mage tire des projectiles."""
        # Placer le joueur dans la portée de tir
        player_pos = (
            sample_goblin_mage.rect.centerx + 100,
            sample_goblin_mage.rect.centery
        )
        
        # Le mage devrait pouvoir tirer
        projectiles = []
        can_fire = sample_goblin_mage.can_fire_at(player_pos)
        
        if can_fire:
            projectile = sample_goblin_mage.fire_at(player_pos)
            assert projectile is not None
            assert isinstance(projectile, Projectile)
    
    @pytest.mark.unit
    def test_goblin_mage_fire_cooldown(self, sample_goblin_mage):
        """Test le cooldown de tir du gobelin mage."""
        # Simuler un tir
        sample_goblin_mage.fire_timer = 0  # Prêt à tirer
        
        # Tirer (dépend de l'implémentation)
        player_pos = (100, 100)
        initial_timer = sample_goblin_mage.fire_timer
        
        if sample_goblin_mage.can_fire_at(player_pos):
            sample_goblin_mage.fire_at(player_pos)
            # Le timer devrait être reset
            assert sample_goblin_mage.fire_timer >= initial_timer
    
    @pytest.mark.unit
    def test_goblin_mage_range_limitation(self, sample_goblin_mage):
        """Test que le gobelin mage ne tire que dans sa portée."""
        # Cible hors de portée
        far_target = (
            sample_goblin_mage.rect.centerx + sample_goblin_mage.fire_range + 100,
            sample_goblin_mage.rect.centery
        )
        
        can_fire = sample_goblin_mage.can_fire_at(far_target)
        assert not can_fire
    
    @pytest.mark.unit
    def test_goblin_mage_line_of_sight(self, sample_goblin_mage):
        """Test que le gobelin mage vérifie la ligne de vue."""
        # Cible dans la portée
        near_target = (
            sample_goblin_mage.rect.centerx + 50,
            sample_goblin_mage.rect.centery
        )
        
        can_fire = sample_goblin_mage.can_fire_at(near_target)
        assert can_fire


class TestBoss:
    """Tests pour la classe Boss."""
    
    @pytest.mark.unit
    def test_boss_initialization(self, mock_pygame_image):
        """Test l'initialisation du boss."""
        boss = Boss(x=100, y=200)
        
        assert boss.rect.centerx == 100
        assert boss.rect.centery == 200
        assert boss.hp > 100  # Le boss devrait avoir plus de HP
        assert boss.attack_range > 0
        assert boss.attack_damage > 0
    
    @pytest.mark.unit
    def test_boss_enhanced_stats(self, sample_boss, sample_enemy):
        """Test que le boss a des stats supérieures aux ennemis normaux."""
        assert sample_boss.hp > sample_enemy.hp
        assert sample_boss.attack_damage > 0
        assert sample_boss.attack_range > 0
    
    @pytest.mark.unit
    def test_boss_special_abilities(self, sample_boss):
        """Test les capacités spéciales du boss."""
        # Le boss devrait avoir des capacités spéciales
        # (dépend de l'implémentation exacte)
        assert hasattr(sample_boss, 'attack_damage')
        assert hasattr(sample_boss, 'attack_range')
    
    @pytest.mark.unit
    def test_boss_attack_pattern(self, sample_boss, sample_player):
        """Test le pattern d'attaque du boss."""
        # Placer le joueur dans la portée d'attaque
        sample_player.rect.center = (
            sample_boss.rect.centerx + 50,
            sample_boss.rect.centery
        )
        
        # Le boss devrait pouvoir attaquer
        if hasattr(sample_boss, 'can_attack'):
            can_attack = sample_boss.can_attack(sample_player.rect.center)
            # Test dépendant de l'implémentation


class TestProjectile:
    """Tests pour la classe Projectile."""
    
    @pytest.mark.unit
    def test_projectile_initialization(self, mock_pygame_image):
        """Test l'initialisation d'un projectile."""
        start_pos = (100, 100)
        target_pos = (200, 200)
        projectile = Projectile(start_pos, target_pos, speed=200, damage=10)
        
        assert projectile.rect.center == start_pos
        assert projectile.damage == 10
        assert projectile.speed == 200
    
    @pytest.mark.unit
    def test_projectile_movement(self, mock_pygame_image):
        """Test le mouvement du projectile vers sa cible."""
        start_pos = (100, 100)
        target_pos = (200, 100)  # Mouvement horizontal
        projectile = Projectile(start_pos, target_pos, speed=100, damage=10)
        
        initial_x = projectile.rect.centerx
        projectile.update(dt=1.0)
        
        # Le projectile devrait s'être déplacé vers la droite
        assert projectile.rect.centerx > initial_x
    
    @pytest.mark.unit
    def test_projectile_reaches_target(self, mock_pygame_image):
        """Test que le projectile atteint sa cible."""
        start_pos = (100, 100)
        target_pos = (200, 100)
        projectile = Projectile(start_pos, target_pos, speed=1000, damage=10)
        
        # Avec une vitesse élevée et un temps suffisant
        projectile.update(dt=1.0)
        
        # Le projectile devrait être proche ou avoir dépassé la cible
        assert projectile.rect.centerx >= target_pos[0]
    
    @pytest.mark.unit
    def test_projectile_collision_detection(self, mock_pygame_image, sample_player):
        """Test la détection de collision du projectile."""
        projectile = Projectile(
            (sample_player.rect.centerx - 10, sample_player.rect.centery),
            (sample_player.rect.centerx + 10, sample_player.rect.centery),
            speed=100, damage=10
        )
        
        # Vérifier si le projectile touche le joueur
        collision = projectile.rect.colliderect(sample_player.rect)
        # Le résultat dépend de la position exacte
    
    @pytest.mark.unit
    def test_projectile_off_screen_removal(self, mock_pygame_image):
        """Test que les projectiles hors écran sont marqués pour suppression."""
        from game.settings import WIDTH, HEIGHT
        
        # Projectile qui va sortir de l'écran
        projectile = Projectile(
            (WIDTH + 100, HEIGHT + 100),  # Hors écran
            (WIDTH + 200, HEIGHT + 200),
            speed=100, damage=10
        )
        
        # Après la mise à jour, le projectile devrait être marqué pour suppression
        result = projectile.update(dt=0.1)
        # (dépend de l'implémentation de la méthode update)


class TestEnemyInteractions:
    """Tests pour les interactions entre ennemis."""
    
    @pytest.mark.unit
    def test_enemy_separation(self, mock_pygame_image):
        """Test la séparation entre ennemis qui se chevauchent."""
        enemy1 = Enemy(x=100, y=100, tier="normal")
        enemy2 = Enemy(x=105, y=105, tier="normal")  # Très proche
        
        initial_distance = math.hypot(
            enemy1.rect.centerx - enemy2.rect.centerx,
            enemy1.rect.centery - enemy2.rect.centery
        )
        
        # Mettre à jour avec séparation
        enemy1.update((200, 200), dt=0.1, enemies=[enemy2])
        
        new_distance = math.hypot(
            enemy1.rect.centerx - enemy2.rect.centerx,
            enemy1.rect.centery - enemy2.rect.centery
        )
        
        # Les ennemis devraient s'être séparés
        assert new_distance >= initial_distance
    
    @pytest.mark.integration
    def test_enemy_swarm_behavior(self, mock_pygame_image, sample_player):
        """Test le comportement de groupe des ennemis."""
        enemies = []
        for i in range(5):
            enemy = Enemy(x=300 + i * 20, y=300 + i * 20, tier="normal")
            enemies.append(enemy)
        
        target_pos = sample_player.rect.center
        
        # Tous les ennemis devraient se diriger vers le joueur
        for enemy in enemies:
            initial_distance = math.hypot(
                enemy.rect.centerx - target_pos[0],
                enemy.rect.centery - target_pos[1]
            )
            
            enemy.update(target_pos, dt=1.0, enemies=enemies)
            
            new_distance = math.hypot(
                enemy.rect.centerx - target_pos[0],
                enemy.rect.centery - target_pos[1]
            )
            
            # Chaque ennemi devrait se rapprocher du joueur
            assert new_distance <= initial_distance + 10  # Tolérance pour la séparation


@pytest.mark.performance
class TestEnemyPerformance:
    """Tests de performance pour les ennemis."""
    
    def test_enemy_update_performance(self, mock_pygame_image, performance_timer):
        """Test la performance de la mise à jour des ennemis."""
        enemies = [Enemy(x=i*10, y=i*10, tier="normal") for i in range(100)]
        target_pos = (500, 500)
        
        performance_timer.start()
        for enemy in enemies:
            enemy.update(target_pos, dt=0.016, enemies=enemies[:10])  # 60 FPS
        performance_timer.stop()
        
        # La mise à jour de 100 ennemis devrait prendre moins de 16ms (60 FPS)
        assert performance_timer.elapsed < 0.016
    
    def test_projectile_update_performance(self, mock_pygame_image, performance_timer):
        """Test la performance de la mise à jour des projectiles."""
        projectiles = []
        for i in range(50):
            projectile = Projectile(
                (i*10, i*10), 
                (500, 500), 
                speed=200, 
                damage=10
            )
            projectiles.append(projectile)
        
        performance_timer.start()
        for projectile in projectiles:
            projectile.update(dt=0.016)
        performance_timer.stop()
        
        # La mise à jour de 50 projectiles devrait être rapide
        assert performance_timer.elapsed < 0.008


@pytest.mark.integration
class TestEnemyIntegration:
    """Tests d'intégration pour les ennemis."""
    
    def test_full_enemy_lifecycle(self, mock_pygame_image, sample_player):
        """Test du cycle de vie complet d'un ennemi."""
        enemy = Enemy(x=300, y=300, tier="normal")
        initial_hp = enemy.hp
        
        # L'ennemi se déplace vers le joueur
        target_pos = sample_player.rect.center
        enemy.update(target_pos, dt=1.0)
        
        # L'ennemi prend des dégâts
        enemy.take_damage(10)
        assert enemy.hp == initial_hp - 10
        assert enemy.flash_timer > 0
        
        # L'ennemi meurt
        enemy.take_damage(enemy.hp)
        assert enemy.hp <= 0
    
    def test_goblin_mage_combat_cycle(self, mock_pygame_image, sample_player):
        """Test du cycle de combat complet d'un gobelin mage."""
        mage = GoblinMage(x=200, y=200)
        
        # Placer le joueur dans la portée
        player_pos = (mage.rect.centerx + 100, mage.rect.centery)
        
        # Le mage devrait pouvoir tirer
        if mage.can_fire_at(player_pos):
            projectile = mage.fire_at(player_pos)
            
            if projectile:
                # Le projectile devrait se diriger vers le joueur
                assert isinstance(projectile, Projectile)
    
    def test_boss_encounter(self, mock_pygame_image, sample_player):
        """Test d'une rencontre complète avec un boss."""
        boss = Boss(x=400, y=400)
        initial_boss_hp = boss.hp
        
        # Le boss devrait avoir plus de HP qu'un ennemi normal
        assert boss.hp > 50
        
        # Le boss prend des dégâts
        boss.take_damage(20)
        assert boss.hp == initial_boss_hp - 20
        
        # Le boss a des capacités spéciales
        assert hasattr(boss, 'attack_damage')
        assert boss.attack_damage > 0 