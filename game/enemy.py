# enemy.py

import pygame
import math
import os
from .settings import MAP_WIDTH, MAP_HEIGHT
from .balance_manager import balance

class Enemy:
    LIFESPAN = 40.0  # secondes

    def __init__(self, x, y, speed=100, tier='normal', player_level=1):
        # moment de spawn
        self.spawn_time = pygame.time.get_ticks() / 1000.0

        # Charger sprites droite/gauche
        base = os.path.join("assets", "gobelin")
        img_r = pygame.image.load(base + "-right.png").convert_alpha()
        img_l = pygame.image.load(base + "-left.png").convert_alpha()

        # Sprite scaling
        sprite_scale = 1.3 if tier != 'normal' else 1.0
        size = (int(80 * sprite_scale), int(80 * sprite_scale))
        self.img_right = pygame.transform.scale(img_r, size)
        self.img_left  = pygame.transform.scale(img_l, size)
        self.image     = self.img_right
        self.rect      = self.image.get_rect(center=(x, y))

        # Coordonnées flottantes pour éviter les problèmes de troncature
        self.float_x = float(self.rect.x)
        self.float_y = float(self.rect.y)

        # NOUVEAU: HP scaling depuis balance.json
        scaling_config = balance.config.get("scaling", {})
        enemy_progression = scaling_config.get("enemy_progression", {})
        
        if tier == 'elite':
            hp_scale = enemy_progression.get("elite_hp_multiplier", 9.0)
        elif tier == 'rare':
            hp_scale = enemy_progression.get("rare_hp_multiplier", 3.0)
        else:
            hp_scale = 1.0
            
        base_hp    = 5
        hp_per_level = enemy_progression.get("hp_per_level", 2)
        self.max_hp = int((base_hp + player_level * hp_per_level) * hp_scale)
        self.hp     = self.max_hp

        # NOUVEAU: Vitesse depuis balance.json
        speed_per_level = enemy_progression.get("speed_per_level", 5)
        self.speed      = speed + player_level * speed_per_level
        self.base_speed = self.speed
        self.slow_timer = 0.0

        # XP & dégâts
        self.xp_value = {'normal':3.5,'rare':10,'elite':15}[tier]
        self.damage   = 1

        # Timers d'attaque
        self.attack_cooldown = 1.0
        self.attack_timer    = 0.0
        self.pause_timer     = 0.0

        # Teinte rare/elite
        if tier == 'rare':
            self.tint_color = (0,0,255,80)
        elif tier == 'elite':
            self.tint_color = (255,255,0,80)
        else:
            self.tint_color = None

        # Flash blanc
        self.flash_duration = 0.2
        self.flash_timer    = 0.0

    def update(self, player_pos, dt):
        # timers attaque/pause/flash
        if self.attack_timer > 0:
            self.attack_timer -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Facteur de pause + slow combinés
        pause_factor = 1.0
        if self.pause_timer > 0:
            self.pause_timer -= dt
            pause_factor = 0.2  # Ralenti à 20% au lieu d'arrêt complet
        
        if self.slow_timer > 0:
            self.slow_timer -= dt
            slow_factor = 0.5
        else:
            slow_factor = 1.0
        
        # Facteur de vitesse combiné
        factor = pause_factor * slow_factor

        # mouvement vers joueur
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.image = self.img_left if dx < 0 else self.img_right
            nx, ny = dx/dist, dy/dist
            
            # Utiliser des coordonnées flottantes pour éviter les problèmes de troncature
            self.float_x += nx * self.base_speed * factor * dt
            self.float_y += ny * self.base_speed * factor * dt

        # Clamp les coordonnées flottantes directement (AVANT conversion entière)
        self.float_x = max(0.0, min(self.float_x, float(MAP_WIDTH - self.rect.width)))
        self.float_y = max(0.0, min(self.float_y, float(MAP_HEIGHT - self.rect.height)))
        
        # Mettre à jour rect avec les valeurs entières clampées
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)

    def draw(self, surface, cam_x, cam_y):
        pos = (self.rect.x - cam_x, self.rect.y - cam_y)
        surface.blit(self.image, pos)
        if self.tint_color:
            mask = pygame.mask.from_surface(self.image)
            tint = mask.to_surface(setcolor=self.tint_color, unsetcolor=(0,0,0,0))
            surface.blit(tint, pos)
        if self.flash_timer > 0:
            mask = pygame.mask.from_surface(self.image)
            flash = mask.to_surface(setcolor=(255,255,255,150), unsetcolor=(0,0,0,0))
            surface.blit(flash, pos)
