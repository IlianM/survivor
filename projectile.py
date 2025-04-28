# projectile.py

import pygame
import math
from settings import MAP_WIDTH, MAP_HEIGHT

class Fireball:
    def __init__(self, x, y, target_pos, speed=300):
        # create a simple circular fireball
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 100, 0), (8, 8), 8)
        self.rect = self.image.get_rect(center=(x, y))
        # compute velocity towards target_pos tuple
        dx, dy = target_pos[0] - x, target_pos[1] - y
        dist = math.hypot(dx, dy) or 1
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed
        # flag for removal on impact or off-screen
        self.hit_target = False

    def update(self, dt):
        # move
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt
        # if outside map bounds, mark for removal
        if self.off_screen():
            self.hit_target = True

    def off_screen(self):
        # returns True if completely outside the logical map
        return (
            self.rect.right  < 0 or
            self.rect.left   > MAP_WIDTH or
            self.rect.bottom < 0 or
            self.rect.top    > MAP_HEIGHT
        )

    def draw(self, surf, cam_x, cam_y):
        surf.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))
