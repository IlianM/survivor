import pytest
import pygame

from game.main import (
    draw_tiled_background,
    draw_bottom_overlay,
    draw_health_globe,
)
from game.main import HEALTH_TEXTURE, HEALTH_ORNAMENT
from game.settings import WIDTH, HEIGHT

@pytest.fixture(autouse=True)
def init_pygame_display(init_pygame):
    # Permet d'utiliser pygame.Surface, convert_alpha(), etc.
    yield

def test_draw_tiled_background_no_error():
    surf = pygame.Surface((WIDTH, HEIGHT))
    # background tuile de 32×32
    bg = pygame.Surface((32, 32))
    for cx, cy in [(0, 0), (15, 20), (-50, -75), (1000, 1000)]:
        draw_tiled_background(surf, cx, cy, bg, 32, 32)

def test_draw_bottom_overlay_position():
    class Dummy:
        def __init__(self):
            self.blit_calls = []
        def blit(self, img, pos):
            self.blit_calls.append((img, pos))

    dummy = Dummy()
    overlay = pygame.Surface((40, 20))
    y_offset = -10
    draw_bottom_overlay(dummy, overlay, y_offset=y_offset, zoom=1.0)
    assert len(dummy.blit_calls) == 1
    img, rect = dummy.blit_calls[0]
    assert img is overlay
    # calcule topleft attendu d'après rect.midbottom = (WIDTH/2, HEIGHT+y_offset)
    mid_x, mid_y = WIDTH // 2, HEIGHT + y_offset
    w, h = overlay.get_size()
    expected = (mid_x - w // 2, mid_y - h)
    assert rect.topleft == expected

@pytest.fixture(autouse=True)
def patch_health_textures(monkeypatch):
    import game.main as gm
    dummy_tex = pygame.Surface((10, 10))
    dummy_orn = pygame.Surface((14, 14), pygame.SRCALPHA)
    monkeypatch.setattr(gm, "HEALTH_TEXTURE", dummy_tex)
    monkeypatch.setattr(gm, "HEALTH_ORNAMENT", dummy_orn)
    yield

@pytest.mark.parametrize("hp_ratio", [0.0, 0.5, 1.0])
def test_draw_health_globe_extremes(hp_ratio):
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    cx, cy, radius = WIDTH // 4, HEIGHT // 3, 30
    draw_health_globe(surf, cx, cy, radius, hp_ratio)
