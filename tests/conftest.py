# tests/conftest.py
import os
import sys
import pytest
import pygame

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
