# player.py

import pygame
import math
import os
from settings import MAP_WIDTH, MAP_HEIGHT

class Player:
    def __init__(self, x, y):
        # — Sons —
        # Assure-toi d'avoir appelé pygame.init() et pygame.mixer.init() avant
        self.attack_sound  = pygame.mixer.Sound(os.path.join("fx", "attack.mp3"))
        self.levelup_sound = pygame.mixer.Sound(os.path.join("fx", "levelup.mp3"))

        # — Sprites & animation —
        horz_height = 128   # hauteur pour gauche/droite
        vert_height =  96   # hauteur pour haut/bas

        # Marche droite (3 frames)
        self.walk_frames_right = []
        for i in range(1, 4):
            img = pygame.image.load(f"assets/knight{i}.png").convert_alpha()
            ow, oh = img.get_size()
            scale = horz_height / oh
            nw = int(ow * scale)
            self.walk_frames_right.append(
                pygame.transform.scale(img, (nw, horz_height))
            )
        # Marche gauche (miroir)
        self.walk_frames_left = [
            pygame.transform.flip(f, True, False)
            for f in self.walk_frames_right
        ]

        # Marche vers le haut (2 frames)
        self.up_frames = []
        for i in range(1, 3):
            img = pygame.image.load(f"assets/knight_up{i}.png").convert_alpha()
            ow, oh = img.get_size()
            scale = vert_height / oh
            nw = int(ow * scale)
            self.up_frames.append(
                pygame.transform.scale(img, (nw, vert_height))
            )

        # Marche vers le bas (2 frames)
        self.down_frames = []
        for i in range(1, 3):
            img = pygame.image.load(f"assets/knightdown_{i}.png").convert_alpha()
            ow, oh = img.get_size()
            scale = vert_height / oh
            nw = int(ow * scale)
            self.down_frames.append(
                pygame.transform.scale(img, (nw, vert_height))
            )

        # Image courante et hitbox
        self.image = self.down_frames[0]
        self.rect  = self.image.get_rect(center=(x, y))

        # Animation
        self.anim_index    = 0
        self.anim_timer    = 0.0
        self.anim_interval = 0.2
        self.direction     = 'down'
        # Décalages verticaux uniquement pour up/down
        self.offset_up     = 20
        self.offset_down   = 15

        # — Stats —
        self.speed   = 170
        self.max_hp  = 10
        self.hp      = self.max_hp
        self.max_arm = 5
        self.armor   = self.max_arm

        # — Attaque —
        self.attack_range        = 120
        self.attack_cooldown     = 1
        self.attack_timer        = 0.0
        self.attack_angle        = 90
        self.attack_damage       = 3
        self.attacking           = False
        self.attack_duration     = 0.2
        self.attack_timer_visual = 0.0
        self.last_attack_angle   = 0

        # — Slash visuel —
        # charge l'image brute orientée sud-ouest
        raw = pygame.image.load(os.path.join("assets", "slash.png")).convert_alpha()
        self.raw_slash   = raw
        # facteur de réduction (0.0 = invisible, 1.0 = taille d'origine)
        self.slash_scale = 0.15

        # — XP & progression —
        self.xp            = 0
        self.level         = 1
        self.next_level_xp = 20
        self.skill_points  = 0
        self.new_level     = False

        # — Auto-attack toggle —
        self.auto_attack = True

    def update(self, keys, dt):
        # — Input & direction & déplacement & animation —
        dx = dy = 0
        if keys[pygame.K_z]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_q]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        # Détection de la direction principale
        if dy < 0:   self.direction = 'up'
        elif dy > 0: self.direction = 'down'
        elif dx < 0: self.direction = 'left'
        elif dx > 0: self.direction = 'right'

        # Normalisation pour vitesse constante en diagonale
        if dx or dy:
            length = math.hypot(dx, dy)
            dx /= length; dy /= length

        # Animation frame
        moving = (dx or dy)
        if moving:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_interval:
                self.anim_timer -= self.anim_interval
                total = max(
                    len(self.walk_frames_right),
                    len(self.walk_frames_left),
                    len(self.up_frames),
                    len(self.down_frames)
                )
                self.anim_index = (self.anim_index + 1) % total
        else:
            self.anim_index = 0
            self.anim_timer = 0

        # Choix du sprite selon la direction
        if self.direction == 'up':
            idx = self.anim_index % len(self.up_frames)
            self.image = self.up_frames[idx]
        elif self.direction == 'down':
            idx = self.anim_index % len(self.down_frames)
            self.image = self.down_frames[idx]
        elif self.direction == 'left':
            idx = self.anim_index % len(self.walk_frames_left)
            self.image = self.walk_frames_left[idx]
        else:  # right
            idx = self.anim_index % len(self.walk_frames_right)
            self.image = self.walk_frames_right[idx]

        # Déplacement + murs invisibles
        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH  - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))

        # Timers d’attaque
        self.attack_timer += dt
        if self.attacking:
            self.attack_timer_visual -= dt
            if self.attack_timer_visual <= 0:
                self.attacking = False

    def can_attack(self):
        return self.attack_timer >= self.attack_cooldown

    def attack(self, enemies, mouse_pos):
        if not self.can_attack():
            return
        # joue le son
        self.attack_sound.play()

        # déclenche visuel & cooldown
        self.attacking           = True
        self.attack_timer        = 0
        self.attack_timer_visual = self.attack_duration

        # calcule l’angle de la souris
        dxm = mouse_pos[0] - self.rect.centerx
        dym = mouse_pos[1] - self.rect.centery
        angle = math.degrees(math.atan2(-dym, dxm)) % 360
        self.last_attack_angle = angle

        # applique dégâts dans le cône
        half = self.attack_angle / 2
        for enemy in enemies:
            dxe = enemy.rect.centerx - self.rect.centerx
            dye = enemy.rect.centery - self.rect.centery
            dist = math.hypot(dxe, dye)
            r = enemy.rect.width / 2
            if dist - r <= self.attack_range:
                a2e  = math.degrees(math.atan2(-dye, dxe)) % 360
                delta = abs((angle - a2e + 180) % 360 - 180)
                if delta <= half:
                    enemy.hp -= self.attack_damage
                    enemy.flash_timer = getattr(enemy, "flash_duration", 0)

    def take_damage(self, amount):
        if self.armor > 0:
            self.armor -= 1
        else:
            self.hp -= amount

    def gain_xp(self, amount):
        bonus = getattr(self, "xp_bonus", 0.0)
        self.xp += int(amount * (1 + bonus))
        while self.xp >= self.next_level_xp:
            self.xp -= self.next_level_xp
            self.level_up()

    def level_up(self):
        self.level += 1
        self.skill_points += 1
        self.next_level_xp = int(self.next_level_xp * 1.15)
        self.new_level     = True
        # joue le son de level-up
        self.levelup_sound.play()
        # bonus auto
        self.max_hp        += 2
        self.hp            += 2
        self.max_arm       += 1
        self.armor         = self.max_arm
        self.attack_damage += 0.8


    # --- Pool réduit d’améliorations ---
    UPGRADE_KEYS = [
        "Strength Boost", "Vitality Surge", "Quick Reflexes",
        "Haste", "Armor Plating", "Extended Reach", "XP Bonus"
    ]

    UPGRADE_INFO = {
        "Strength Boost":   {"type":"flat",   "value": 2.5,  "unit":"Damage"},
        "Vitality Surge":   {"type":"flat",   "value": 5,    "unit":"Max HP"},
        "Quick Reflexes":   {"type":"mult",   "value": 0.7,  "unit":"Cooldown"},
        "Haste":            {"type":"mult",   "value": 1.3,  "unit":"Speed"},
        "Armor Plating":    {"type":"flat",   "value": 5,    "unit":"Armor"},
        "Extended Reach":   {"type":"flat",   "value":20,    "unit":"Range"},
        "XP Bonus":         {"type":"percent","value": 0.20, "unit":"XP"}
    }

    def apply_upgrade(self, key):
        if key == "Strength Boost":
            self.attack_damage += 2.5
        elif key == "Vitality Surge":
            self.max_hp += 5
            self.hp     += 5
        elif key == "Quick Reflexes":
            self.attack_cooldown *= 0.7
        elif key == "Haste":
            self.speed *= 1.3
        elif key == "Armor Plating":
            self.max_arm += 5
            self.armor   += 5
        elif key == "Extended Reach":
            self.attack_range += 20
        elif key == "XP Bonus":
            self.xp_bonus = getattr(self, "xp_bonus", 0) + 0.20

    def draw(self, surface, cam_x, cam_y):
        # calcule y_off pour up/down uniquement
        if   self.direction == 'up':
            y_off = self.offset_up
        elif self.direction == 'down':
            y_off = self.offset_down
        else:
            y_off = 0

        # dessine le joueur
        surface.blit(
            self.image,
            (self.rect.x - cam_x,
             self.rect.y - cam_y + y_off)
        )

        # si en attaque, dessine le slash tourné et réduit
        if self.attacking:
            # rotation : slash.png origine SW=225°
            rot = self.last_attack_angle - 225
            slash = pygame.transform.rotozoom(
                self.raw_slash, rot, self.slash_scale
            )
            sw, sh = slash.get_size()
            # décalage devant le joueur
            rad     = math.radians(self.last_attack_angle)
            dx_off  = math.cos(rad) * (self.attack_range * 0.5)
            dy_off  = -math.sin(rad) * (self.attack_range * 0.5)
            pos_x   = self.rect.centerx + dx_off - sw//2 - cam_x
            pos_y   = self.rect.centery + dy_off - sh//2 - cam_y + y_off
            surface.blit(slash, (pos_x, pos_y))
