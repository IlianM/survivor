import pygame
import pytest
from game.main import get_cri_icons, ICON_SIZE

@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    pygame.display.set_mode((200,200))
    yield
    pygame.quit()

def test_get_cri_icons_loads_surfaces_and_font():
    icon, icon_gray, font = get_cri_icons()
    assert isinstance(icon, pygame.Surface)
    assert isinstance(icon_gray, pygame.Surface)
    assert icon.get_size() == (ICON_SIZE, ICON_SIZE)
    assert icon_gray.get_size() == (ICON_SIZE, ICON_SIZE)
    # test qu'au moins un pixel ne soit pas entièrement transparent
    assert icon.get_at((0,0)).a != 0 or icon.get_at((ICON_SIZE-1,ICON_SIZE-1)).a != 0
    # font doit pouvoir rendre du texte
    surf = font.render("0", True, (255,255,255))
    assert isinstance(surf, pygame.Surface)
