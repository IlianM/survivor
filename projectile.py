# projectile.py
import pygame
import math

class Fireball:
    def __init__(self, x, y, target_pos, speed=300):
        self.image = pygame.Surface((16,16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255,100,0), (8,8), 8)
        self.rect = self.image.get_rect(center=(x,y))
        dx, dy = target_pos[0]-x, target_pos[1]-y
        dist = math.hypot(dx, dy) or 1
        self.vx = dx/dist * speed
        self.vy = dy/dist * speed

    def update(self, dt):
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt

    def draw(self, surf, cam_x, cam_y):
        surf.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))
