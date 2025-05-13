import pytest
from game.settings import WIDTH, HEIGHT, FPS, MAP_WIDTH, MAP_HEIGHT

def test_settings_values():
    # Dimensions d'écran
    assert isinstance(WIDTH, (int, float)) and WIDTH > 0, f"WIDTH doit être positif, got {WIDTH}"
    assert isinstance(HEIGHT, (int, float)) and HEIGHT > 0, f"HEIGHT doit être positif, got {HEIGHT}"

    # Framerate
    assert isinstance(FPS, (int, float)) and FPS > 0, f"FPS doit être positif, got {FPS}"

    # Taille de la carte
    assert isinstance(MAP_WIDTH, (int, float)) and MAP_WIDTH > 0, f"MAP_WIDTH doit être positif, got {MAP_WIDTH}"
    assert isinstance(MAP_HEIGHT, (int, float)) and MAP_HEIGHT > 0, f"MAP_HEIGHT doit être positif, got {MAP_HEIGHT}"

    # La carte doit être au moins aussi grande que l'écran
    assert MAP_WIDTH >= WIDTH, f"MAP_WIDTH ({MAP_WIDTH}) doit être ≥ WIDTH ({WIDTH})"
    assert MAP_HEIGHT >= HEIGHT, f"MAP_HEIGHT ({MAP_HEIGHT}) doit être ≥ HEIGHT ({HEIGHT})"
