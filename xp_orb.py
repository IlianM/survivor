# xp_orb.py

import pygame
import math
import os

class XPOrb:
    def __init__(self, x, y, value):
        self.value = value

                # son de ramassage
        pickup_path = os.path.join("fx", "xp_orb.mp3")
        self.pickup_sound = pygame.mixer.Sound(pickup_path)

        # un petit cercle doré de 16×16 px
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 215, 0), (8, 8), 8)
        self.rect = self.image.get_rect(center=(x, y))

        # paramètres d’attraction
        self.attract_radius = 200   # px à partir desquels l’orb s’attire
        self.attract_speed  = 150   # px/s

    def update(self, dt, player_pos):
        # distance au joueur
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        # si dans le rayon d’attraction, on se rapproche
        if 0 < dist < self.attract_radius:
            nx, ny = dx / dist, dy / dist
            self.rect.x += nx * self.attract_speed * dt
            self.rect.y += ny * self.attract_speed * dt

    def draw(self, surface, cam_x, cam_y):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))
