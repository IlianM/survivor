# tests/test_strategic_validation.py
"""
Tests stratégiques pour optimisation, validation fonctionnelle et debug facile.
Objectifs : Performance, fonctionnalités critiques, détection rapide des régressions.
"""
import pytest
import pygame
import time
import math
from unittest.mock import Mock, patch
from game.player import Player


class TestCriticalGameplayFeatures:
    """Tests des fonctionnalités critiques qui cassent le jeu si elles échouent."""
    
    @pytest.mark.unit
    def test_player_can_move_correctly(self, sample_player, dummy_keys):
        """Test critique: Le joueur peut-il bouger dans toutes les directions?"""
        initial_pos = (sample_player.rect.x, sample_player.rect.y)
        
        # Test mouvement de base
        movements = [
            (pygame.K_d, 'right'),  # Droite
            (pygame.K_q, 'left'),   # Gauche  
            (pygame.K_z, 'up'),     # Haut
            (pygame.K_s, 'down')    # Bas
        ]
        
        for key, direction in movements:
            # Reset position
            sample_player.rect.x, sample_player.rect.y = initial_pos
            
            # Activer le mouvement
            for k in dummy_keys: dummy_keys[k] = False
            dummy_keys[key] = True
            
            sample_player.update(dummy_keys, dt=1.0)  # 1 seconde = mouvement visible
            
            # Vérifier que le joueur a bougé ET dans la bonne direction
            moved = (sample_player.rect.x != initial_pos[0] or 
                    sample_player.rect.y != initial_pos[1])
            assert moved, f"Le joueur ne bouge pas avec la touche {direction}"
            assert sample_player.direction == direction
    
    @pytest.mark.unit  
    def test_player_can_attack_enemies(self, sample_player):
        """Test critique: Le joueur peut-il attaquer et infliger des dégâts?"""
        # Créer un vrai ennemi mock avec les propriétés nécessaires
        enemy = Mock()
        enemy.rect = pygame.Rect(150, 100, 20, 20)  # Proche du joueur
        enemy.hp = 100
        enemy.take_damage = Mock()
        
        # Le joueur doit pouvoir attaquer
        sample_player.attack_timer = sample_player.attack_cooldown  # Prêt
        mouse_pos = (150, 100)  # Vers l'ennemi
        
        sample_player.attack([enemy], mouse_pos)
        
        # Vérifier que l'attaque a eu lieu
        assert sample_player.attacking, "L'attaque ne se déclenche pas"
        assert sample_player.attack_timer == 0, "Le cooldown ne se reset pas"
        enemy.take_damage.assert_called_once_with(sample_player.attack_damage)
    
    @pytest.mark.unit
    def test_player_levels_up_correctly(self, sample_player):
        """Test critique: Le système de progression fonctionne-t-il?"""
        initial_level = sample_player.level
        initial_damage = sample_player.attack_damage
        
        # Gagner exactement assez d'XP pour level up
        xp_needed = sample_player.next_level_xp - sample_player.xp
        sample_player.gain_xp(xp_needed)
        
        assert sample_player.level == initial_level + 1, "Le level up ne fonctionne pas"
        assert sample_player.attack_damage > initial_damage, "Les stats n'augmentent pas"
        assert sample_player.new_level, "Le flag new_level n'est pas set"
    
    @pytest.mark.unit
    def test_player_dash_functionality(self, sample_player, dummy_keys):
        """Test critique: Le dash fonctionne-t-il correctement?"""
        initial_x = sample_player.rect.x
        
        # Setup dash
        sample_player.dash_timer = 0.0  # Prêt à dash
        dummy_keys[pygame.K_d] = True   # Direction
        dummy_keys[pygame.K_SPACE] = True  # Dash
        
        # 1er update: Active le dash
        sample_player.update(dummy_keys, dt=0.1)
        
        # Vérifier que le dash est activé
        assert sample_player.dash_time_left > 0, "Le dash ne s'active pas"
        assert sample_player.dash_timer > 0, "Le cooldown du dash ne s'active pas"
        
        # 2ème update: Le dash devrait maintenant bouger le joueur
        dummy_keys[pygame.K_SPACE] = False  # Relâcher la touche
        sample_player.update(dummy_keys, dt=0.1)
        
        # Le joueur devrait avoir bougé pendant le dash
        distance_moved = abs(sample_player.rect.x - initial_x)
        expected_dash_distance = sample_player.dash_speed * 0.1
        
        assert distance_moved > 0, "Le joueur ne bouge pas pendant le dash"
        # Vérifier que la distance est proche de l'attendu (tolérance pour les calculs)
        assert abs(distance_moved - expected_dash_distance) < 10, f"Distance dash incorrecte: {distance_moved} vs {expected_dash_distance}"


class TestPerformanceCritical:
    """Tests de performance pour identifier les goulots d'étranglement."""
    
    @pytest.mark.performance
    def test_player_update_performance(self, sample_player, dummy_keys):
        """Performance critique: update() du joueur est-elle assez rapide?"""
        # Simuler 60 FPS pendant 1 seconde = 60 updates
        dummy_keys[pygame.K_d] = True  # Mouvement constant
        
        start_time = time.perf_counter()
        
        for _ in range(60):
            sample_player.update(dummy_keys, dt=1/60)
        
        elapsed = time.perf_counter() - start_time
        
        # 60 updates devraient prendre moins de 16ms (budget 60 FPS)
        assert elapsed < 0.016, f"Player.update() trop lent: {elapsed*1000:.1f}ms pour 60 frames"
        
        # Calcul par frame
        per_frame = elapsed / 60
        print(f"Performance Player.update(): {per_frame*1000:.3f}ms par frame")
        
        # Seuil d'alerte
        if per_frame > 0.001:  # Plus de 1ms par frame
            pytest.warn(f"Player.update() utilise {per_frame*1000:.1f}ms/frame - optimisation recommandée")
    
    @pytest.mark.performance  
    def test_attack_calculation_performance(self, sample_player):
        """Performance critique: Les calculs d'attaque sont-ils optimisés?"""
        # Créer beaucoup d'ennemis pour stresser le système
        enemies = []
        for i in range(50):  # 50 ennemis
            enemy = Mock()
            enemy.rect = pygame.Rect(100 + i*5, 100 + i*5, 20, 20)
            enemy.hp = 100
            enemy.take_damage = Mock()
            enemies.append(enemy)
        
        sample_player.attack_timer = sample_player.attack_cooldown
        mouse_pos = (200, 200)
        
        start_time = time.perf_counter()
        sample_player.attack(enemies, mouse_pos)
        elapsed = time.perf_counter() - start_time
        
        # L'attaque avec 50 ennemis devrait prendre moins de 1ms
        assert elapsed < 0.001, f"Attack() trop lent avec 50 ennemis: {elapsed*1000:.1f}ms"
        print(f"Performance Attack: {elapsed*1000:.3f}ms pour 50 ennemis")
    
    @pytest.mark.performance
    def test_memory_efficiency(self, sample_player):
        """Test d'efficacité mémoire - détection des fuites."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Simuler une session de jeu intensive
        dummy_keys = {pygame.K_d: True}
        for _ in range(1000):  # 1000 frames
            sample_player.update(dummy_keys, dt=0.016)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # L'augmentation ne devrait pas dépasser 1MB pour 1000 frames
        assert memory_increase < 1024*1024, f"Fuite mémoire détectée: +{memory_increase/1024:.0f}KB"
        print(f"Consommation mémoire: +{memory_increase/1024:.1f}KB pour 1000 frames")


class TestRegressionDetection:
    """Tests pour détecter rapidement les régressions lors de modifications."""
    
    @pytest.mark.unit
    def test_player_stats_consistency(self, sample_player):
        """Détection de régression: Les stats du joueur sont-elles cohérentes?"""
        # Ces valeurs ne devraient jamais changer par accident
        assert sample_player.speed > 0, "Vitesse du joueur incorrecte"
        assert sample_player.max_hp > 0, "HP max du joueur incorrect"
        assert sample_player.attack_damage > 0, "Dégâts d'attaque incorrects"
        assert sample_player.attack_range > 0, "Portée d'attaque incorrecte"
        assert 0 < sample_player.attack_cooldown < 10, "Cooldown d'attaque anormal"
        
        # Ratios de cohérence
        assert sample_player.hp <= sample_player.max_hp, "HP actuel > HP max"
        assert sample_player.level >= 1, "Niveau invalide"
        assert sample_player.xp >= 0, "XP négatif"
    
    @pytest.mark.unit
    def test_player_boundaries_respected(self, sample_player, dummy_keys):
        """Détection de régression: Le joueur reste-t-il dans les limites?"""
        from game.settings import MAP_WIDTH, MAP_HEIGHT
        
        # Forcer le joueur aux bords extrêmes
        test_positions = [
            (0, 0),                                    # Coin haut-gauche
            (MAP_WIDTH-50, 0),                        # Coin haut-droit  
            (0, MAP_HEIGHT-50),                       # Coin bas-gauche
            (MAP_WIDTH-50, MAP_HEIGHT-50)             # Coin bas-droit
        ]
        
        for x, y in test_positions:
            sample_player.rect.x = x
            sample_player.rect.y = y
            
            # Essayer de sortir des limites
            dummy_keys[pygame.K_q] = True  # Gauche
            dummy_keys[pygame.K_z] = True  # Haut
            
            sample_player.update(dummy_keys, dt=10.0)  # Gros dt
            
            # Vérifier que le joueur reste dans les limites
            assert 0 <= sample_player.rect.x <= MAP_WIDTH - sample_player.rect.width
            assert 0 <= sample_player.rect.y <= MAP_HEIGHT - sample_player.rect.height
    
    @pytest.mark.unit
    def test_upgrade_system_integrity(self, sample_player):
        """Détection de régression: Le système d'upgrade fonctionne-t-il?"""
        # Test de tous les upgrades sans erreur
        upgrades = ["Strength Boost", "Vitality Surge", "Quick Reflexes", 
                   "Haste", "Extended Reach", "XP Bonus"]
        
        for upgrade in upgrades:
            try:
                sample_player.apply_upgrade(upgrade)
            except Exception as e:
                pytest.fail(f"Upgrade '{upgrade}' a causé une erreur: {e}")
        
        # Vérifier que les stats ont bien augmenté
        assert sample_player.attack_damage >= 3 + 3  # Initial + Strength Boost minimum
        assert sample_player.max_hp >= 10 + 5       # Initial + Vitality Surge minimum


class TestDebugHelpers:
    """Tests pour faciliter le debug lors de problèmes."""
    
    @pytest.mark.unit
    def test_player_state_dump(self, sample_player):
        """Helper de debug: Dump complet de l'état du joueur."""
        state = {
            'position': (sample_player.rect.x, sample_player.rect.y),
            'hp': f"{sample_player.hp}/{sample_player.max_hp}",
            'level': sample_player.level,
            'xp': f"{sample_player.xp}/{sample_player.next_level_xp}",
            'stats': {
                'damage': sample_player.attack_damage,
                'speed': sample_player.speed,
                'range': sample_player.attack_range,
                'cooldown': sample_player.attack_cooldown
            },
            'timers': {
                'attack': sample_player.attack_timer,
                'dash': sample_player.dash_timer,
                'scream': sample_player.scream_timer
            },
            'flags': {
                'attacking': sample_player.attacking,
                'magnet_active': sample_player.magnet_active,
                'show_scream_cone': sample_player.show_scream_cone
            }
        }
        
        print(f"\n🔍 DEBUG - État du joueur:")
        for category, data in state.items():
            print(f"  {category}: {data}")
        
        # Ce test passe toujours, il sert juste au debug
        assert True
    
    @pytest.mark.unit
    def test_input_response_debug(self, sample_player, dummy_keys):
        """Helper de debug: Vérifier la réponse aux inputs."""
        inputs_tested = []
        
        test_inputs = [
            (pygame.K_z, "up"),
            (pygame.K_s, "down"), 
            (pygame.K_q, "left"),
            (pygame.K_d, "right"),
            (pygame.K_SPACE, "dash")
        ]
        
        for key, action in test_inputs:
            # Reset
            for k in dummy_keys: dummy_keys[k] = False
            sample_player.dash_timer = 0.0
            
            # Test input
            dummy_keys[key] = True
            old_pos = (sample_player.rect.x, sample_player.rect.y)
            old_direction = sample_player.direction
            
            sample_player.update(dummy_keys, dt=0.1)
            
            # Analyser la réponse
            pos_changed = (sample_player.rect.x != old_pos[0] or 
                          sample_player.rect.y != old_pos[1])
            direction_changed = sample_player.direction != old_direction
            dash_active = sample_player.dash_time_left > 0
            
            result = {
                'input': action,
                'position_changed': pos_changed,
                'direction_changed': direction_changed,
                'dash_activated': dash_active if action == "dash" else None
            }
            inputs_tested.append(result)
        
        print(f"\n🎮 DEBUG - Réponse aux inputs:")
        for result in inputs_tested:
            print(f"  {result}")
        
        assert True  # Test informatif


# Test d'intégration critique
@pytest.mark.integration  
def test_complete_gameplay_cycle(sample_player):
    """Test d'intégration: Un cycle complet de gameplay fonctionne-t-il?"""
    # Simuler un petit cycle de gameplay
    
    # 1. Joueur se déplace
    keys = {pygame.K_d: True}
    sample_player.update(keys, dt=1.0)
    moved = sample_player.rect.x > 100  # Position initiale
    
    # 2. Joueur attaque
    enemy = Mock()
    enemy.rect = pygame.Rect(200, 100, 20, 20)
    enemy.take_damage = Mock()
    sample_player.attack_timer = sample_player.attack_cooldown
    sample_player.attack([enemy], (200, 100))
    
    # 3. Joueur gagne de l'XP
    initial_xp = sample_player.xp
    sample_player.gain_xp(50)
    
    # 4. Joueur utilise une amélioration
    sample_player.apply_upgrade("Strength Boost")
    
    # Vérifier que tout a fonctionné
    assert moved, "Le mouvement a échoué"
    assert enemy.take_damage.called, "L'attaque a échoué"  
    assert sample_player.xp > initial_xp, "Le gain d'XP a échoué"
    assert sample_player.attack_damage > 3, "L'upgrade a échoué"
    
    print("✅ Cycle de gameplay complet validé") 