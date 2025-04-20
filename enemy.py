import pygame
import math
import os
from settings import MAP_WIDTH, MAP_HEIGHT

class Enemy:
    def __init__(self, x, y, speed=100, xp_value=1):
        # Charger les deux sens de sprite
        base = os.path.join("assets", "gobelin")
        img_right = pygame.image.load(base + "-right.png").convert_alpha()
        img_left  = pygame.image.load(base + "-left.png").convert_alpha()

        # Redimensionner
        self.img_right = pygame.transform.scale(img_right, (80, 80))
        self.img_left  = pygame.transform.scale(img_left,  (80, 80))
        # Image courante
        self.image = self.img_right
        self.rect = self.image.get_rect(center=(x, y))

        # Mouvement
        self.speed = speed

        # Points de vie
        self.max_hp = 3
        self.hp = self.max_hp

        # Dégâts
        self.damage = 1
        self.xp_value = xp_value

    def update(self, player_pos, dt):
        # Calcul de la direction vers le joueur
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            # Choix du sprite selon le signe de dx
            if dx < 0:
                self.image = self.img_left
            else:
                self.image = self.img_right

            # Normalisation et déplacement
            nx, ny = dx / dist, dy / dist
            self.rect.x += nx * self.speed * dt
            self.rect.y += ny * self.speed * dt

        # “Murs invisibles” pour rester dans la map
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))

    def draw(self, surface, cam_x, cam_y):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))
