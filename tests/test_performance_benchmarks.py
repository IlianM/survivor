# tests/test_performance_benchmarks.py
import pytest
import pygame
import time
import statistics
from unittest.mock import Mock, patch
from game.player import Player
from game.enemy import Enemy


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Tests de performance pour identifier les optimisations nécessaires."""
    
    def test_player_update_benchmark(self, performance_timer, dummy_keys):
        """Benchmark de la mise à jour du joueur."""
        test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        with patch('pygame.mixer.Sound'), \
             patch('pygame.image.load') as mock_image, \
             patch('pygame.freetype.Font'):
            
            mock_image.return_value = test_surface
            player = Player(x=100, y=100)
            
            # Mesurer plusieurs exécutions
            times = []
            for _ in range(100):
                performance_timer.start()
                player.update(dummy_keys, dt=0.016)  # 60 FPS
                performance_timer.stop()
                times.append(performance_timer.elapsed)
            
            avg_time = statistics.mean(times)
            max_time = max(times)
            
            print(f"\nPlayer.update() avg: {avg_time*1000:.3f}ms, max: {max_time*1000:.3f}ms")
            
            # Une mise à jour devrait prendre moins de 1ms en moyenne
            assert avg_time < 0.001
    
    def test_enemy_update_benchmark(self, performance_timer):
        """Benchmark de la mise à jour des ennemis."""
        test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        with patch('pygame.image.load') as mock_image:
            mock_image.return_value = test_surface
            
            # Créer plusieurs ennemis
            enemies = [Enemy(x=i*50, y=i*50, tier="normal") for i in range(10)]
            target_pos = (500, 500)
            
            times = []
            for _ in range(50):
                performance_timer.start()
                for enemy in enemies:
                    enemy.update(target_pos, dt=0.016, enemies=enemies)
                performance_timer.stop()
                times.append(performance_timer.elapsed)
            
            avg_time = statistics.mean(times)
            max_time = max(times)
            
            print(f"\n10 enemies update avg: {avg_time*1000:.3f}ms, max: {max_time*1000:.3f}ms")
            
            # La mise à jour de 10 ennemis ne devrait pas prendre plus de 2ms
            assert avg_time < 0.002
    
    def test_collision_detection_benchmark(self, performance_timer):
        """Benchmark de la détection de collision."""
        test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        with patch('pygame.mixer.Sound'), \
             patch('pygame.image.load') as mock_image, \
             patch('pygame.freetype.Font'):
            
            mock_image.return_value = test_surface
            
            player = Player(x=400, y=400)
            enemies = [Enemy(x=i*20+300, y=j*20+300, tier="normal") 
                      for i in range(10) for j in range(10)]  # 100 ennemis
            
            times = []
            for _ in range(100):
                performance_timer.start()
                
                # Test de collision avec tous les ennemis
                collisions = 0
                for enemy in enemies:
                    if player.rect.colliderect(enemy.rect):
                        collisions += 1
                
                performance_timer.stop()
                times.append(performance_timer.elapsed)
            
            avg_time = statistics.mean(times)
            print(f"\nCollision detection (100 enemies) avg: {avg_time*1000:.3f}ms")
            
            # Détection de collision avec 100 ennemis < 0.5ms
            assert avg_time < 0.0005
    
    def test_memory_usage_benchmark(self):
        """Test d'utilisation mémoire pour détecter les fuites."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        with patch('pygame.image.load') as mock_image:
            mock_image.return_value = test_surface
            
            # Créer et détruire beaucoup d'objets
            for i in range(1000):
                enemy = Enemy(x=i, y=i, tier="normal")
                del enemy
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            print(f"\nMemory increase after 1000 enemy creations: {memory_increase/1024/1024:.2f}MB")
            
            # L'augmentation de mémoire ne devrait pas être excessive
            assert memory_increase < 50 * 1024 * 1024  # 50MB max
    
    def test_attack_calculation_benchmark(self, performance_timer):
        """Benchmark du calcul d'attaque."""
        test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        with patch('pygame.mixer.Sound'), \
             patch('pygame.image.load') as mock_image, \
             patch('pygame.freetype.Font'):
            
            mock_image.return_value = test_surface
            
            player = Player(x=400, y=400)
            enemies = [Enemy(x=i*30+300, y=j*30+300, tier="normal") 
                      for i in range(5) for j in range(5)]  # 25 ennemis
            
            times = []
            for _ in range(100):
                performance_timer.start()
                player.attack(enemies, (450, 450))
                performance_timer.stop()
                times.append(performance_timer.elapsed)
            
            avg_time = statistics.mean(times)
            print(f"\nAttack calculation (25 enemies) avg: {avg_time*1000:.3f}ms")
            
            # Calcul d'attaque avec 25 ennemis < 1ms
            assert avg_time < 0.001


@pytest.mark.performance
class TestScalabilityBenchmarks:
    """Tests de scalabilité pour différents nombres d'entités."""
    
    @pytest.mark.parametrize("enemy_count", [10, 50, 100, 200])
    def test_enemy_scaling(self, performance_timer, enemy_count):
        """Test de scalabilité avec différents nombres d'ennemis."""
        test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        with patch('pygame.image.load') as mock_image:
            mock_image.return_value = test_surface
            
            enemies = [Enemy(x=i*10, y=i*10, tier="normal") for i in range(enemy_count)]
            target_pos = (500, 500)
            
            performance_timer.start()
            for enemy in enemies:
                enemy.update(target_pos, dt=0.016)
            performance_timer.stop()
            
            time_per_enemy = performance_timer.elapsed / enemy_count
            print(f"\n{enemy_count} enemies: {performance_timer.elapsed*1000:.3f}ms total, "
                  f"{time_per_enemy*1000000:.1f}µs per enemy")
            
            # Le temps par ennemi ne devrait pas augmenter de façon excessive
            assert time_per_enemy < 0.0001  # 100µs par ennemi max
    
    def test_frame_rate_consistency(self, performance_timer):
        """Test de cohérence du frame rate."""
        test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        with patch('pygame.mixer.Sound'), \
             patch('pygame.image.load') as mock_image, \
             patch('pygame.freetype.Font'):
            
            mock_image.return_value = test_surface
            
            player = Player(x=400, y=400)
            enemies = [Enemy(x=i*20, y=i*20, tier="normal") for i in range(50)]
            
            frame_times = []
            dummy_keys = {pygame.K_d: True}  # Mouvement constant
            
            # Simuler 60 frames
            for frame in range(60):
                performance_timer.start()
                
                # Simulation d'une frame complète
                player.update(dummy_keys, dt=0.016)
                for enemy in enemies:
                    enemy.update(player.rect.center, dt=0.016, enemies=enemies)
                
                performance_timer.stop()
                frame_times.append(performance_timer.elapsed)
            
            avg_frame_time = statistics.mean(frame_times)
            max_frame_time = max(frame_times)
            std_dev = statistics.stdev(frame_times)
            
            print(f"\nFrame times - avg: {avg_frame_time*1000:.3f}ms, "
                  f"max: {max_frame_time*1000:.3f}ms, std_dev: {std_dev*1000:.3f}ms")
            
            # Temps de frame cohérent pour 60 FPS
            assert avg_frame_time < 0.016  # Moins de 16ms en moyenne
            assert std_dev < 0.005  # Faible variation


@pytest.mark.slow
class TestStressTests:
    """Tests de stress pour pousser le système aux limites."""
    
    def test_massive_enemy_count(self, performance_timer):
        """Test avec un très grand nombre d'ennemis."""
        test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        with patch('pygame.image.load') as mock_image:
            mock_image.return_value = test_surface
            
            # Créer 1000 ennemis
            enemies = []
            performance_timer.start()
            
            for i in range(1000):
                enemy = Enemy(x=i%100*20, y=i//100*20, tier="normal")
                enemies.append(enemy)
            
            performance_timer.stop()
            creation_time = performance_timer.elapsed
            
            print(f"\nCreated 1000 enemies in {creation_time*1000:.1f}ms")
            
            # Test de mise à jour
            target_pos = (1000, 1000)
            performance_timer.start()
            
            for enemy in enemies[:100]:  # Tester seulement les 100 premiers
                enemy.update(target_pos, dt=0.016)
            
            performance_timer.stop()
            update_time = performance_timer.elapsed
            
            print(f"Updated 100/1000 enemies in {update_time*1000:.1f}ms")
            
            # Vérifications de performance
            assert creation_time < 1.0  # Création < 1s
            assert update_time < 0.01   # Mise à jour < 10ms
    
    def test_long_running_session(self, performance_timer):
        """Test d'une session de jeu longue pour détecter les dégradations."""
        test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        with patch('pygame.mixer.Sound'), \
             patch('pygame.image.load') as mock_image, \
             patch('pygame.freetype.Font'):
            
            mock_image.return_value = test_surface
            
            player = Player(x=400, y=400)
            enemies = [Enemy(x=i*50, y=i*50, tier="normal") for i in range(20)]
            
            # Simuler 10 secondes de jeu (600 frames à 60 FPS)
            frame_times = []
            dummy_keys = {pygame.K_d: True}
            
            for frame in range(600):
                performance_timer.start()
                
                player.update(dummy_keys, dt=0.016)
                for enemy in enemies:
                    enemy.update(player.rect.center, dt=0.016)
                
                performance_timer.stop()
                frame_times.append(performance_timer.elapsed)
                
                # Enregistrer seulement quelques mesures pour éviter la surcharge
                if frame % 100 == 0:
                    recent_avg = statistics.mean(frame_times[-100:])
                    print(f"Frame {frame}: avg time = {recent_avg*1000:.3f}ms")
            
            # Analyser la dégradation de performance
            first_100 = statistics.mean(frame_times[:100])
            last_100 = statistics.mean(frame_times[-100:])
            degradation = (last_100 - first_100) / first_100
            
            print(f"\nPerformance degradation over 10s: {degradation*100:.1f}%")
            
            # La dégradation ne devrait pas dépasser 20%
            assert degradation < 0.20


@pytest.mark.performance
class TestMemoryOptimization:
    """Tests pour l'optimisation mémoire."""
    
    def test_object_pooling_effectiveness(self):
        """Test l'efficacité du pooling d'objets si implémenté."""
        # Ce test sera utile si on implémente un système de pooling
        pass
    
    def test_texture_memory_usage(self):
        """Test l'utilisation mémoire des textures."""
        # Mesurer l'impact des textures sur la mémoire
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Créer plusieurs surfaces
        surfaces = []
        for i in range(100):
            surface = pygame.Surface((64, 64), pygame.SRCALPHA)
            surface.fill((i % 255, (i*2) % 255, (i*3) % 255))
            surfaces.append(surface)
        
        final_memory = process.memory_info().rss
        memory_per_surface = (final_memory - initial_memory) / len(surfaces)
        
        print(f"\nMemory per 64x64 surface: {memory_per_surface/1024:.1f}KB")
        
        # Nettoyer
        del surfaces
        
        # Une surface 64x64 RGBA ne devrait pas prendre plus de 20KB
        assert memory_per_surface < 20 * 1024 