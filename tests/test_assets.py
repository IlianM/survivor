import os
import glob
import pytest
import pygame

# Construit le chemin vers la racine du projet
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ASSET_DIR = os.path.join(ROOT, "assets")
FX_DIR    = os.path.join(ROOT, "fx")
FONT_DIR  = os.path.join(ASSET_DIR, "fonts")

def test_assets_images_exist():
    """Toutes les images listées doivent exister dans assets/."""
    images = [
        "knight1.png", "knight2.png", "knight3.png",
        "knight_up1.png", "knight_up2.png",
        "knightdown_1.png", "knightdown_2.png",
        "background.png", "main_menu.png",
        "bottom_overlay.png", "health_orb_ornement.png",
        "health_texture.png", "magnet.png",
        "upgrade_card.png", "slash.png",
        "gobelin_mage.png"
    ]
    for img in images:
        path = os.path.join(ASSET_DIR, img)
        assert os.path.exists(path), f"Image manquante : {path}"

def test_assets_sounds_loadable():
    """Tous les fichiers .mp3/.wav de fx/ doivent pouvoir être chargés par pygame.mixer."""
    # récupère tous les .mp3 et .wav dans fx/
    patterns = [os.path.join(FX_DIR, "*.mp3"), os.path.join(FX_DIR, "*.wav")]
    sound_files = []
    for pat in patterns:
        sound_files.extend(glob.glob(pat))

    for snd in sound_files:
        try:
            _ = pygame.mixer.Sound(snd)
        except Exception as e:
            pytest.fail(f"Impossible de charger le son {snd} : {e}")

def test_fonts_loadable():
    """Toutes les polices .ttf de assets/fonts/ doivent pouvoir être chargées par pygame.freetype."""
    ttf_files = glob.glob(os.path.join(FONT_DIR, "*.ttf"))
    assert ttf_files, f"Aucune police trouvée dans {FONT_DIR}"
    for font_path in ttf_files:
        try:
            _ = pygame.freetype.Font(font_path, 12)
        except Exception as e:
            pytest.fail(f"Impossible de charger la police {font_path} : {e}")
