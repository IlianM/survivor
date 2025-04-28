# goblin_mage.py

import pygame
import os
import math

from settings import MAP_WIDTH, MAP_HEIGHT, WIDTH, HEIGHT
from projectile import Fireball

class GoblinMage:
    def __init__(self, x, y):
        # --- Chargement et mise à l’échelle du sprite ---
        raw = pygame.image.load(
            os.path.join("assets", "gobelin_mage.png")
        ).convert_alpha()
        scale = 0.2
        w, h = raw.get_size()
        self.image = pygame.transform.scale(raw, (int(w*scale), int(h*scale)))
        self.rect  = self.image.get_rect(center=(x, y))

        # --- Stats & timers ---
        self.max_hp        = 4
        self.hp            = self.max_hp
        self.xp_value      = 10
        self.fire_cooldown = 5.0
        self.fire_timer    = 0.0
        self.projectiles   = []

        # Flash blanc
        self.flash_duration = 0.2
        self.flash_timer    = 0.0

        # Mouvement “zone d’attaque”
        self.speed   = 50  # px/s
        self.min_mul = 3.0
        self.max_mul = 4.0

    def update(self, player, dt, cam_x, cam_y):
        # --- 1) Mouvement pour rester dans [min_dist, max_dist] ---
        px, py = player.rect.center
        dx, dy = px - self.rect.centerx, py - self.rect.centery
        dist = math.hypot(dx, dy) or 1

        desired_min = player.attack_range * self.min_mul
        desired_max = player.attack_range * self.max_mul

        if dist > desired_max:
            nx, ny = dx/dist, dy/dist
            self.rect.x += nx * self.speed * dt
            self.rect.y += ny * self.speed * dt
        elif dist < desired_min:
            nx, ny = -dx/dist, -dy/dist
            self.rect.x += nx * self.speed * dt
            self.rect.y += ny * self.speed * dt

        # Clamp aux limites de la carte
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH  - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))

        # --- 2) Tir de boule de feu si cooldown écoulé ET mage à l’écran ---
        screen_x = self.rect.x - cam_x
        screen_y = self.rect.y - cam_y
        on_screen = (
            -self.rect.width  < screen_x < WIDTH and
            -self.rect.height < screen_y < HEIGHT
        )

        self.fire_timer -= dt
        if self.fire_timer <= 0:
            if on_screen:
                fx, fy = self.rect.center
                self.projectiles.append(Fireball(fx, fy, (px, py)))
            self.fire_timer = self.fire_cooldown

        # --- 3) Update des projectiles ---
        for fb in self.projectiles[:]:
            fb.update(dt)
            if not (0 <= fb.rect.x <= MAP_WIDTH and 0 <= fb.rect.y <= MAP_HEIGHT):
                self.projectiles.remove(fb)

        # --- 4) Décrément du flash blanc ---
        if self.flash_timer > 0:
            self.flash_timer -= dt

    def draw(self, surf, cam_x, cam_y):
        # Position à l’écran
        ex = self.rect.x - cam_x
        ey = self.rect.y - cam_y

        # 1) Sprite principal
        surf.blit(self.image, (ex, ey))

        # 2) Flash blanc
        if self.flash_timer > 0:
            mask = pygame.mask.from_surface(self.image)
            flash_surf = mask.to_surface(
                setcolor=(255,255,255,150),
                unsetcolor=(0,0,0,0)
            )
            surf.blit(flash_surf, (ex, ey))

        # 3) Barre de vie
        bw, bh = self.rect.width, 5
        bar_x, bar_y = ex, ey - bh - 2
        pygame.draw.rect(surf, (100,0,0), (bar_x, bar_y, bw, bh))
        hp_ratio = max(self.hp, 0) / self.max_hp
        pygame.draw.rect(surf, (0,200,0), (bar_x, bar_y, bw * hp_ratio, bh))
        pygame.draw.rect(surf, (255,255,255), (bar_x, bar_y, bw, bh), 1)

        # 4) Projectiles
        for fb in self.projectiles:
            fb.draw(surf, cam_x, cam_y)
