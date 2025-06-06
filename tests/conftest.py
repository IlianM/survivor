# tests/conftest.py
import os
import sys
import pytest
import pygame
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Tuple

# 1) Dummy drivers pour audio / vidéo
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_VIDEODRIVER"] = "dummy"

# 2) On ajoute la racine du projet au PYTHONPATH
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

@pytest.fixture(scope="session", autouse=True)
def init_pygame():
    """
    Fixture qui initialise pygame AVANT les tests et
    crée une mini-fenêtre 1×1 pour les convert_alpha().
    """
    pygame.init()
    pygame.mixer.init()
    pygame.freetype.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()

@pytest.fixture
def mock_pygame_sound():
    """Mock pygame.mixer.Sound pour éviter les erreurs de fichiers audio manquants."""
    with patch('pygame.mixer.Sound') as mock_sound:
        mock_instance = Mock()
        mock_instance.play = Mock()
        mock_sound.return_value = mock_instance
        yield mock_sound

@pytest.fixture
def mock_pygame_image():
    """Mock pygame.image.load pour éviter les erreurs de fichiers image manquants."""
    # Créer une vraie surface pygame
    test_surface = pygame.Surface((64, 64), pygame.SRCALPHA)
    test_surface.fill((255, 255, 255, 255))  # Surface blanche transparente
    
    with patch('pygame.image.load') as mock_load:
        mock_load.return_value = test_surface
        yield mock_load

@pytest.fixture
def mock_pygame_transform():
    """Mock pygame.transform pour éviter les erreurs de transformation."""
    with patch('pygame.transform.scale') as mock_scale, \
         patch('pygame.transform.flip') as mock_flip, \
         patch('pygame.transform.rotozoom') as mock_rotozoom:
        
        # Retourner la surface d'origine pour scale
        mock_scale.side_effect = lambda surf, size: surf
        mock_flip.side_effect = lambda surf, x, y: surf
        mock_rotozoom.side_effect = lambda surf, angle, scale: surf
        
        yield (mock_scale, mock_flip, mock_rotozoom)

@pytest.fixture
def mock_pygame_freetype():
    """Mock pygame.freetype.Font pour éviter les erreurs de font."""
    with patch('pygame.freetype.Font') as mock_font:
        mock_instance = Mock()
        mock_instance.render.return_value = (Mock(), Mock())
        mock_font.return_value = mock_instance
        yield mock_font

@pytest.fixture
def sample_player():
    """Fixture pour créer un joueur avec des paramètres standards pour les tests."""
    from game.player import Player
    
    # Créer des vraies surfaces pygame minimales
    test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    
    with patch('pygame.mixer.Sound') as mock_sound, \
         patch('pygame.image.load') as mock_image, \
         patch('pygame.freetype.Font') as mock_font:
        
        # Configuration des mocks
        mock_sound.return_value = Mock()
        mock_image.return_value = test_surface
        mock_font.return_value = Mock()
        
        # Créer le joueur
        player = Player(x=100, y=100)
        player.hp = player.max_hp = 100
        player.level = 1
        player.xp = 0
        player.next_level_xp = 100
        # Reset timers
        player.attack_timer = player.attack_cooldown
        player.dash_timer = 0
        player.scream_timer = 0
        player.dash_time_left = 0
        player.show_scream_cone = False
        return player

@pytest.fixture
def sample_enemy():
    """Fixture pour créer un ennemi de test."""
    from game.enemy import Enemy
    
    test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    
    with patch('pygame.image.load') as mock_image:
        mock_image.return_value = test_surface
        enemy = Enemy(x=200, y=200, tier="normal")
        enemy.hp = 50
        return enemy

@pytest.fixture
def sample_goblin_mage():
    """Fixture pour créer un gobelin mage de test."""
    from game.goblin_mage import GoblinMage
    
    test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    
    with patch('pygame.image.load') as mock_image:
        mock_image.return_value = test_surface
        mage = GoblinMage(x=300, y=300)
        mage.hp = 30
        return mage

@pytest.fixture
def sample_boss():
    """Fixture pour créer un boss de test."""
    from game.boss import Boss
    
    test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    
    with patch('pygame.image.load') as mock_image:
        mock_image.return_value = test_surface
        boss = Boss(x=400, y=400)
        boss.hp = 200
        return boss

@pytest.fixture
def dummy_keys() -> Dict[int, bool]:
    """Fixture pour créer un dictionnaire de touches pressées par défaut."""
    return {
        pygame.K_z: False,
        pygame.K_q: False, 
        pygame.K_s: False,
        pygame.K_d: False,
        pygame.K_SPACE: False,
        pygame.K_c: False,
        pygame.K_y: False,
        pygame.K_k: False,
        pygame.K_ESCAPE: False
    }

@pytest.fixture
def mock_surface():
    """Mock d'une surface pygame pour les tests de rendu."""
    surface = Mock()
    surface.get_width.return_value = 800
    surface.get_height.return_value = 600
    surface.get_size.return_value = (800, 600)
    surface.blit = Mock()
    surface.fill = Mock()
    return surface

@pytest.fixture
def game_state_data():
    """Données d'état de jeu pour les tests."""
    return {
        'level': 1,
        'enemies_killed': 0,
        'game_time': 0.0,
        'wave_number': 1,
        'spawn_timer': 0.0,
        'enemies': [],
        'mages': [],
        'bosses': [],
        'xp_orbs': [],
        'projectiles': []
    }

@pytest.fixture
def mock_font():
    """Mock d'une font pygame."""
    font = Mock()
    font.render.return_value = (Mock(), Mock())
    return font

# Fixtures pour les tests de performance
@pytest.fixture
def performance_timer():
    """Utilitaire pour mesurer les performances."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
            
        def stop(self):
            self.end_time = time.perf_counter()
            
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0
    
    return Timer()

# Fixtures d'intégration
@pytest.fixture
def integration_setup():
    """Setup pour les tests d'intégration."""
    test_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    
    # Mock tous les fichiers externes nécessaires
    with patch('pygame.mixer.Sound') as mock_sound, \
         patch('pygame.image.load') as mock_image, \
         patch('pygame.freetype.Font') as mock_font:
        
        mock_sound.return_value = Mock()
        mock_image.return_value = test_surface
        mock_font.return_value = Mock()
        
        yield
