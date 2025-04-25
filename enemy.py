# enemy.py

import pygame
import math
import os
from settings import MAP_WIDTH, MAP_HEIGHT

class Enemy:
    def __init__(self, x, y, speed=100, tier='normal', player_level=1):
        # Charger les sprites droite/gauche
        base = os.path.join("assets", "gobelin")
        img_r = pygame.image.load(base + "-right.png").convert_alpha()
        img_l = pygame.image.load(base + "-left.png").convert_alpha()

        # --- Sprite scaling ---
        # normal = ×1.0, rare & elite = ×1.3
        sprite_scale = 1.3 if tier != 'normal' else 1.0
        size = (int(80 * sprite_scale), int(80 * sprite_scale))
        self.img_right = pygame.transform.scale(img_r, size)
        self.img_left  = pygame.transform.scale(img_l, size)
        self.image     = self.img_right
        self.rect      = self.image.get_rect(center=(x, y))

        # --- HP scaling ---
        # normal = ×1.0, rare = ×3.0, elite = ×9.0
        if tier == 'elite':
            hp_scale = 9.0
        elif tier == 'rare':
            hp_scale = 3.0
        else:
            hp_scale = 1.0

        base_hp    = 3
        self.max_hp = int((base_hp + player_level * 2) * hp_scale)
        self.hp     = self.max_hp

        # Vitesse
        self.speed  = speed + player_level * 5

        # XP et dégâts
        self.xp_value = {'normal': 2, 'rare': 10, 'elite': 15}[tier]
        self.damage   = 1

        # Timers d’attaque
        self.attack_cooldown = 1.0
        self.attack_timer    = 0.0
        self.pause_timer     = 0.0

        # Teinte pour rare/elite
        if tier == 'rare':
            self.tint_color = (0, 0, 255, 80)
        elif tier == 'elite':
            self.tint_color = (255, 255, 0, 80)
        else:
            self.tint_color = None

        # Flash blanc à la prise de dégât
        self.flash_duration = 0.2
        self.flash_timer    = 0.0

    def update(self, player_pos, dt):
        # Décrémente les timers
        if self.attack_timer > 0:
            self.attack_timer -= dt
        if self.pause_timer > 0:
            self.pause_timer -= dt
            return

        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Mouvement vers le joueur
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.image = self.img_left if dx < 0 else self.img_right
            nx, ny = dx / dist, dy / dist
            self.rect.x += nx * self.speed * dt
            self.rect.y += ny * self.speed * dt

        # Contrainte aux limites de la map
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))

    def draw(self, surface, cam_x, cam_y):
        pos = (self.rect.x - cam_x, self.rect.y - cam_y)
        # Sprite principal
        surface.blit(self.image, pos)

        # Teinte si rare/elite (pixels opaques seulement)
        if self.tint_color:
            mask = pygame.mask.from_surface(self.image)
            tint_surf = mask.to_surface(
                setcolor=self.tint_color,
                unsetcolor=(0,0,0,0)
            )
            surface.blit(tint_surf, pos)

        # Flash blanc si dégât (pixels opaques seulement)
        if self.flash_timer > 0:
            mask = pygame.mask.from_surface(self.image)
            flash_surf = mask.to_surface(
                setcolor=(255,255,255,150),
                unsetcolor=(0,0,0,0)
            )
            surface.blit(flash_surf, pos)
