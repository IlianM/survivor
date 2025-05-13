import pytest
from game.main import BASE_MAX_ENEMIES, PER_LEVEL_ENEMIES

def cap_for_level(level):
    return BASE_MAX_ENEMIES + PER_LEVEL_ENEMIES * (level - 1)

def can_spawn(current_enemies, level):
    return current_enemies < cap_for_level(level)

@pytest.mark.parametrize("level,expected_cap", [
    (1, BASE_MAX_ENEMIES),
    (2, BASE_MAX_ENEMIES + PER_LEVEL_ENEMIES),
    (5, BASE_MAX_ENEMIES + PER_LEVEL_ENEMIES * 4),
    (10, BASE_MAX_ENEMIES + PER_LEVEL_ENEMIES * 9),
])
def test_cap_formula(level, expected_cap):
    assert cap_for_level(level) == expected_cap

@pytest.mark.parametrize("level", [1, 3, 7])
def test_spawn_allowed_below_cap(level):
    cap = cap_for_level(level)
    # juste en dessous du cap => on peut spawner
    assert can_spawn(cap - 1, level) is True

@pytest.mark.parametrize("level", [1, 3, 7])
def test_spawn_blocked_at_or_above_cap(level):
    cap = cap_for_level(level)
    # à ou au-dessus du cap => on ne spawne plus
    assert can_spawn(cap, level) is False
    assert can_spawn(cap + 5, level) is False
