# goblin_mage.py

import os
import math
import pygame
from .settings import MAP_WIDTH, MAP_HEIGHT, WIDTH, HEIGHT
from .projectile import Fireball
from .utils import resource_path

class GoblinMage:
    def __init__(self, x, y):
        # — Charger & scaler le sprite du mage —
        raw = pygame.image.load(resource_path("assets/gobelin_mage.png")).convert_alpha()
        scale_factor = 0.18  # ajustez pour plus petit ou plus grand
        iw, ih = raw.get_size()
        sw, sh = int(iw * scale_factor), int(ih * scale_factor)
        self.image = pygame.transform.scale(raw, (sw, sh))
        self.rect  = self.image.get_rect(center=(x, y))

        # — Stats & timers —
        self.base_speed       = 80
        self.slow_timer       = 0.0
        self.slow_factor      = 0.5

        self.fire_cooldown    = 5.0
        self.fire_timer       = 0.0

        self.projectiles      = []

        # HP, XP & dégâts
        self.max_hp           = 6
        self.hp               = self.max_hp
        self.xp_value         = 12
        self.damage           = 2

        # Flash blanc lors de la hit
        self.flash_duration   = 0.2
        self.flash_timer      = 0.0

        # zone de tir (multiples de la portée du joueur)
        self.min_mul          = 3.0
        self.max_mul          = 4.0

    def take_damage(self, amount):
        # Applique les PV et déclenche le flash
        self.hp -= amount
        self.flash_timer = self.flash_duration

    def update(self, player, dt, cam_x, cam_y):
        # 1) Timers
        if self.fire_timer > 0:
            self.fire_timer -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.slow_timer > 0:
            self.slow_timer -= dt
            speed_factor = self.slow_factor
        else:
            speed_factor = 1.0

        # 2) Mouvement selon distance
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery  - self.rect.centery
        dist = math.hypot(dx, dy) or 1
        nx, ny = dx/dist, dy/dist

        desired_min = getattr(player, "attack_range", 50) * self.min_mul
        desired_max = getattr(player, "attack_range", 50) * self.max_mul
        move = self.base_speed * speed_factor * dt

        if dist > desired_max:
            self.rect.x += nx * move
            self.rect.y += ny * move
        elif dist < desired_min:
            self.rect.x -= nx * move
            self.rect.y -= ny * move
        # sinon reste en place

        # Clamp aux limites de la map
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH  - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))

        # 3) Tir si à l’écran et cooldown terminé
        on_screen = (
            -self.rect.width  < self.rect.x - cam_x < WIDTH and
            -self.rect.height < self.rect.y - cam_y < HEIGHT
        )
        if on_screen and self.fire_timer <= 0:
            self.fire_timer = self.fire_cooldown
            fx, fy = player.rect.center
            self.projectiles.append(
                Fireball(self.rect.centerx, self.rect.centery, (fx, fy))
            )

        # 4) Update projectiles
        for fb in self.projectiles[:]:
            fb.update(dt)
            if fb.off_screen() or getattr(fb, "hit_target", False):
                self.projectiles.remove(fb)

    def draw(self, surface, cam_x, cam_y):
        # 1) Sprite
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))

        # 2) Flash blanc respectant la forme du sprite
        if self.flash_timer > 0:
            mask = pygame.mask.from_surface(self.image)
            flash_surf = mask.to_surface(
                setcolor=(255,255,255,150),
                unsetcolor=(0,0,0,0)
            )
            surface.blit(flash_surf, (self.rect.x - cam_x, self.rect.y - cam_y))

        # 3) Barre de PV
        bar_w, bar_h = self.rect.width, 5
        bx = self.rect.x - cam_x
        by = self.rect.y - cam_y - bar_h - 2
        pygame.draw.rect(surface, (100, 0, 0), (bx, by, bar_w, bar_h))
        hp_ratio = max(0, self.hp) / self.max_hp
        pygame.draw.rect(surface, (0, 200, 0), (bx, by, bar_w * hp_ratio, bar_h))

        # 4) Projectiles
        for fb in self.projectiles:
            fb.draw(surface, cam_x, cam_y)
