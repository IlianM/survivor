import pytest
from game.settings import WIDTH, HEIGHT, MAP_WIDTH, MAP_HEIGHT

def clamp_camera(px, py):
    """Reproduit la logique de clamp de la caméra du main loop."""
    cam_x = max(0, min(px - WIDTH // 2, MAP_WIDTH - WIDTH))
    cam_y = max(0, min(py - HEIGHT // 2, MAP_HEIGHT - HEIGHT))
    return cam_x, cam_y

@pytest.mark.parametrize("px,py,exp_x,exp_y", [
    (0, 0, 0, 0),
    (MAP_WIDTH, 0, MAP_WIDTH - WIDTH, 0),
    (0, MAP_HEIGHT, 0, MAP_HEIGHT - HEIGHT),
    (MAP_WIDTH, MAP_HEIGHT, MAP_WIDTH - WIDTH, MAP_HEIGHT - HEIGHT),
])
def test_camera_positions(px, py, exp_x, exp_y):
    cam_x, cam_y = clamp_camera(px, py)
    assert cam_x == exp_x
    assert cam_y == exp_y

@pytest.mark.parametrize("px,py", [
    (-100, -100),
    (MAP_WIDTH + 100, MAP_HEIGHT + 100),
])
def test_camera_clamp_out_of_bounds(px, py):
    cam_x, cam_y = clamp_camera(px, py)
    assert 0 <= cam_x <= MAP_WIDTH - WIDTH
    assert 0 <= cam_y <= MAP_HEIGHT - HEIGHT
