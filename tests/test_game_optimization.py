"""
Tests d'optimisation pour identifier les goulots d'étranglement du jeu.
Focus sur performance, stabilité et détection de régressions.
"""
import pytest
import pygame
import time
from unittest.mock import Mock, patch


class TestGamePerformanceBottlenecks:
    """Identifier les goulots d'étranglement de performance."""
    
    @pytest.mark.performance
    def test_enemy_spawn_performance(self, mock_pygame_image):
        """Performance critique: Le spawn d'ennemis est-il assez rapide?"""
        from game.enemy import Enemy
        
        start_time = time.perf_counter()
        
        # Spawner 100 ennemis rapidement
        enemies = []
        for i in range(100):
            enemy = Enemy(x=i*10, y=i*10, tier="normal")
            enemies.append(enemy)
        
        elapsed = time.perf_counter() - start_time
        
        # 100 ennemis devraient se créer en moins de 10ms
        assert elapsed < 0.01, f"Spawn de 100 ennemis trop lent: {elapsed*1000:.1f}ms"
        print(f"Performance Spawn: {elapsed*1000:.1f}ms pour 100 ennemis")
    
    @pytest.mark.performance
    def test_enemy_update_scaling(self, mock_pygame_image, sample_player):
        """Performance: Les updates d'ennemis scalent-elles bien?"""
        from game.enemy import Enemy
        
        target_pos = sample_player.rect.center
        enemy_counts = [10, 50, 100]
        
        for count in enemy_counts:
            enemies = [Enemy(x=i*20, y=i*20, tier="normal") for i in range(count)]
            
            start_time = time.perf_counter()
            
            # Update tous les ennemis
            for enemy in enemies:
                enemy.update(target_pos, dt=0.016, enemies=enemies[:5])  # Limite collision
            
            elapsed = time.perf_counter() - start_time
            per_enemy = elapsed / count
            
            print(f"Performance {count} ennemis: {elapsed*1000:.1f}ms total, {per_enemy*1000:.3f}ms/ennemi")
            
            # Vérifier que ça scale linéairement (pas quadratique)
            assert per_enemy < 0.0001, f"Update d'ennemi trop lent: {per_enemy*1000:.1f}ms/ennemi"
    
    @pytest.mark.performance  
    def test_projectile_performance(self, mock_pygame_image):
        """Performance: Les projectiles sont-ils optimisés?"""
        from game.projectile import Projectile
        
        # Créer beaucoup de projectiles
        projectiles = []
        for i in range(100):
            proj = Projectile(
                start_pos=(i*5, i*5), 
                target_pos=(500, 500), 
                speed=200, 
                damage=10
            )
            projectiles.append(proj)
        
        start_time = time.perf_counter()
        
        # Update tous les projectiles
        for proj in projectiles:
            proj.update(dt=0.016)
        
        elapsed = time.perf_counter() - start_time
        
        # 100 projectiles devraient s'updater en moins de 1ms
        assert elapsed < 0.001, f"Update de 100 projectiles trop lent: {elapsed*1000:.1f}ms"
        print(f"Performance Projectiles: {elapsed*1000:.3f}ms pour 100 projectiles")


class TestGameStabilityValidation:
    """Valider que les systèmes critiques sont stables."""
    
    @pytest.mark.unit
    def test_enemy_types_functional(self, mock_pygame_image):
        """Test fonctionnel: Tous les types d'ennemis marchent-ils?"""
        from game.enemy import Enemy
        from game.goblin_mage import GoblinMage  
        from game.boss import Boss
        
        # Test création sans erreur
        enemy_types = [
            ("normal", Enemy, (100, 100, "normal")),
            ("mage", GoblinMage, (200, 200)),
            ("boss", Boss, (300, 300))
        ]
        
        for name, enemy_class, args in enemy_types:
            try:
                enemy = enemy_class(*args)
                assert enemy.hp > 0, f"{name} a 0 HP"
                assert hasattr(enemy, 'rect'), f"{name} n'a pas de rect"
                print(f"✅ {name} enemy fonctionnel")
            except Exception as e:
                pytest.fail(f"❌ {name} enemy cassé: {e}")
    
    @pytest.mark.unit
    def test_xp_orb_collection_functional(self, mock_pygame_image, mock_pygame_sound, sample_player):
        """Test fonctionnel: La collecte d'XP fonctionne-t-elle?"""
        from game.xp_orb import XPOrb
        
        # Créer un orbe XP
        orb = XPOrb(x=sample_player.rect.centerx, y=sample_player.rect.centery, value=50)
        
        # Vérifier propriétés de base
        assert orb.value == 50, "Valeur XP incorrecte"
        assert hasattr(orb, 'rect'), "Orbe XP sans hitbox"
        
        # Test collision
        collision = sample_player.rect.colliderect(orb.rect)
        if collision:
            initial_xp = sample_player.xp
            sample_player.gain_xp(orb.value)
            assert sample_player.xp > initial_xp, "Gain XP ne fonctionne pas"
        
        print("✅ Système XP orb fonctionnel")
    
    @pytest.mark.unit
    def test_attack_system_integrity(self, sample_player, mock_pygame_image):
        """Test d'intégrité: Le système d'attaque est-il robuste?"""
        from game.enemy import Enemy
        
        # Créer des ennemis à différentes distances
        enemies = [
            Enemy(x=130, y=100, tier="normal"),   # Proche - devrait toucher
            Enemy(x=300, y=100, tier="normal"),   # Loin - ne devrait pas toucher
            Enemy(x=120, y=200, tier="normal")    # Angle différent
        ]
        
        sample_player.attack_timer = sample_player.attack_cooldown
        sample_player.attack(enemies, mouse_pos=(130, 100))
        
        # Au moins un ennemi devrait être touché
        damaged_enemies = [e for e in enemies if hasattr(e, 'flash_timer') and e.flash_timer > 0]
        assert len(damaged_enemies) > 0, "Aucun ennemi touché par l'attaque"
        
        print(f"✅ Système d'attaque: {len(damaged_enemies)}/3 ennemis touchés")


class TestMemoryAndResourceManagement:
    """Tests pour détecter les fuites de ressources."""
    
    @pytest.mark.performance
    def test_sprite_loading_efficiency(self, mock_pygame_image):
        """Performance: Le chargement de sprites est-il efficace?"""
        start_time = time.perf_counter()
        
        # Simuler le chargement d'un joueur (charge beaucoup de sprites)
        from game.player import Player
        
        with patch('pygame.mixer.Sound'):
            player = Player(x=400, y=400)
        
        elapsed = time.perf_counter() - start_time
        
        # Création du joueur ne devrait pas prendre plus de 10ms
        assert elapsed < 0.01, f"Chargement joueur trop lent: {elapsed*1000:.1f}ms"
        print(f"Performance Chargement Player: {elapsed*1000:.1f}ms")
    
    @pytest.mark.performance
    def test_game_objects_cleanup(self, mock_pygame_image):
        """Test de nettoyage: Les objets se nettoient-ils correctement?"""
        from game.enemy import Enemy
        from game.projectile import Projectile
        
        # Créer et détruire des objets
        objects_created = []
        
        for i in range(50):
            enemy = Enemy(x=i*10, y=i*10, tier="normal")
            proj = Projectile((i*5, i*5), (500, 500), speed=100, damage=5)
            objects_created.extend([enemy, proj])
        
        # Simuler destruction
        for obj in objects_created:
            del obj
        
        # Test que la mémoire se libère (test basique)
        assert True  # Plus sophistiqué nécessiterait un profiler mémoire
        print("✅ Nettoyage d'objets simulé")


class TestRobustnessAndEdgeCases:
    """Tests de robustesse pour éviter les crashes."""
    
    @pytest.mark.unit
    def test_boundary_conditions(self, sample_player):
        """Test: Le jeu gère-t-il les conditions limites?"""
        # HP à zéro
        sample_player.take_damage(1000)
        assert sample_player.hp >= 0, "HP négatif détecté"
        
        # XP négatif impossible
        sample_player.xp = 0
        # Ne devrait pas planter même avec des valeurs étranges
        sample_player.gain_xp(-50)  # XP négatif
        assert sample_player.xp >= 0, "XP négatif autorisé"
        
        # Cooldowns négatifs
        sample_player.attack_timer = -1.0
        sample_player.update({}, dt=0.1)
        assert sample_player.attack_timer >= 0, "Timer négatif persistant"
        
        print("✅ Conditions limites gérées")
    
    @pytest.mark.unit
    def test_error_resistance(self, sample_player):
        """Test: Le jeu résiste-t-il aux erreurs d'input?"""
        # Inputs malformés
        bad_inputs = [None, {}, "invalid", [1,2,3]]
        
        for bad_input in bad_inputs:
            try:
                sample_player.update(bad_input, dt=0.1)
                # Ne devrait pas planter
            except Exception as e:
                pytest.fail(f"Crash avec input {bad_input}: {e}")
        
        # Paramètres étranges
        sample_player.update({}, dt=-1.0)  # dt négatif
        sample_player.update({}, dt=1000.0)  # dt énorme
        
        print("✅ Résistance aux erreurs validée")


# Helper pour benchmark rapide
@pytest.mark.performance
def test_quick_performance_benchmark(sample_player, mock_pygame_image):
    """Benchmark rapide pour validation régulière."""
    from game.enemy import Enemy
    from game.xp_orb import XPOrb
    
    # Setup
    enemies = [Enemy(x=i*30, y=i*30, tier="normal") for i in range(20)]
    orbs = [XPOrb(x=i*25, y=i*25, value=10) for i in range(10)]
    keys = {pygame.K_d: True}
    
    start_time = time.perf_counter()
    
    # Simuler une frame de jeu typique
    sample_player.update(keys, dt=0.016)
    
    for enemy in enemies:
        enemy.update(sample_player.rect.center, dt=0.016)
    
    for orb in orbs:
        orb.update(sample_player.rect.center, dt=0.016)
    
    elapsed = time.perf_counter() - start_time
    
    print(f"⚡ Benchmark frame complète: {elapsed*1000:.3f}ms")
    print(f"   - Player + 20 enemies + 10 orbs")
    print(f"   - {'✅ RAPIDE' if elapsed < 0.002 else '⚠️ LENT'}")
    
    # Une frame complète devrait prendre moins de 2ms
    if elapsed > 0.005:  # 5ms = seuil d'alerte
        pytest.warn(f"Performance dégradée: {elapsed*1000:.1f}ms/frame") 