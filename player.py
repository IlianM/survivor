# player.py

import pygame
import math
import os
from settings import MAP_WIDTH, MAP_HEIGHT

class Player:
    def __init__(self, x, y):
        # — Sons —
        self.attack_sound   = pygame.mixer.Sound(os.path.join("fx", "attack.mp3"))
        self.levelup_sound  = pygame.mixer.Sound(os.path.join("fx", "levelup.mp3"))
        self.scream_sound   = pygame.mixer.Sound(os.path.join("fx", "eagle_scream.mp3"))

        # — Sprites & animation —
        horz_height = 128
        vert_height = 96

        # droite (3 frames)
        self.walk_frames_right = []
        for i in range(1, 4):
            img = pygame.image.load(f"assets/knight{i}.png").convert_alpha()
            ow, oh = img.get_size()
            scale = horz_height / oh
            nw = int(ow * scale)
            self.walk_frames_right.append(pygame.transform.scale(img, (nw, horz_height)))
        self.walk_frames_left = [pygame.transform.flip(f, True, False) for f in self.walk_frames_right]

        # haut (2 frames)
        self.up_frames = []
        for i in range(1, 3):
            img = pygame.image.load(f"assets/knight_up{i}.png").convert_alpha()
            ow, oh = img.get_size()
            scale = vert_height / oh
            nw = int(ow * scale)
            self.up_frames.append(pygame.transform.scale(img, (nw, vert_height)))

        # bas (2 frames)
        self.down_frames = []
        for i in range(1, 3):
            img = pygame.image.load(f"assets/knightdown_{i}.png").convert_alpha()
            ow, oh = img.get_size()
            scale = vert_height / oh
            nw = int(ow * scale)
            self.down_frames.append(pygame.transform.scale(img, (nw, vert_height)))

        # image initiale & hitbox
        self.image = self.down_frames[0]
        self.rect  = self.image.get_rect(center=(x, y))

        # animation
        self.anim_index    = 0
        self.anim_timer    = 0.0
        self.anim_interval = 0.2
        self.direction     = 'down'
        self.offset_up     = 20
        self.offset_down   = 15

        # stats
        self.speed   = 170
        self.max_hp  = 10
        self.hp      = self.max_hp
        self.max_arm = 5
        self.armor   = self.max_arm

        # attaque
        self.attack_range        = 120
        self.attack_cooldown     = 1.0
        self.attack_angle        = 90
        self.attack_timer        = 0.0
        self.attack_damage       = 3
        self.attacking           = False
        self.attack_duration     = 0.2
        self.attack_timer_visual = 0.0
        self.last_attack_angle   = 0

        # slash visuel
        raw = pygame.image.load(os.path.join("assets", "slash.png")).convert_alpha()
        self.raw_slash   = raw
        self.slash_scale = 0.15

        # XP & progression
        self.xp            = 0
        self.level         = 1
        self.next_level_xp = 20
        self.skill_points  = 0
        self.new_level     = False
        self.xp_bonus      = 0.0

        # auto‐attack
        self.auto_attack = True

        # dash
        self.dash_cooldown  = 2.0
        self.dash_timer     = 0.0
        self.dash_duration  = 0.2
        self.dash_time_left = 0.0
        self.dash_speed     = 800
        self.dash_dir       = (0, 0)

        # cri
        self.scream_cooldown      = 10.0
        self.scream_timer         = 0.0
        self.scream_damage        = 1
        self.scream_range         = self.attack_range * 3
        self.scream_slow_duration = 3.0
        self.scream_slow_factor   = 0.6


        # Aimant
        self.magnet_active   = False
        self.magnet_timer    = 0.0
        self.magnet_duration = 8.0   # durée de l’effet en secondes

        # affichage du cône
        self.show_scream_cone   = False
        self.scream_cone_timer  = 0.0
        self.scream_angle       = 0.0

    def update(self, keys, dt):
        # — Timer du bonus Aimant —
        if self.magnet_active:
            self.magnet_timer -= dt
            if self.magnet_timer <= 0:
                self.magnet_active = False

        # 1) timers attaque, dash, cri
        self.attack_timer = min(self.attack_timer + dt, self.attack_cooldown)
        if self.attacking:
            self.attack_timer_visual -= dt
            if self.attack_timer_visual <= 0:
                self.attacking = False

        if self.dash_timer > 0:
            self.dash_timer -= dt
        if self.scream_timer > 0:
            self.scream_timer -= dt
        if self.show_scream_cone:
            self.scream_cone_timer -= dt
            if self.scream_cone_timer <= 0:
                self.show_scream_cone = False

        # 2) dash en cours
        if self.dash_time_left > 0:
            self.dash_time_left -= dt
            self.rect.x += self.dash_dir[0] * self.dash_speed * dt
            self.rect.y += self.dash_dir[1] * self.dash_speed * dt
            self.rect.x = max(0, min(self.rect.x, MAP_WIDTH  - self.rect.width))
            self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))
            return

        # 3) déplacement
        dx = dy = 0
        if keys[pygame.K_z]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_q]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        if dx or dy:
            length = math.hypot(dx, dy)
            dx /= length; dy /= length

        # 4) dash déclenché
        if keys[pygame.K_SPACE] and self.dash_timer <= 0:
            if dx or dy:
                self.dash_dir = (dx, dy)
            else:
                dir_map = {'up':(0,-1),'down':(0,1),'left':(-1,0),'right':(1,0)}
                self.dash_dir = dir_map[self.direction]
            self.dash_time_left = self.dash_duration
            self.dash_timer     = self.dash_cooldown
            return

        # 5) animation marche
        if dy < 0:    self.direction = 'up'
        elif dy > 0:  self.direction = 'down'
        elif dx < 0:  self.direction = 'left'
        elif dx > 0:  self.direction = 'right'

        moving = (dx or dy)
        if moving:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_interval:
                self.anim_timer -= self.anim_interval
                total = max(len(self.walk_frames_right),
                            len(self.walk_frames_left),
                            len(self.up_frames),
                            len(self.down_frames))
                self.anim_index = (self.anim_index + 1) % total
        else:
            self.anim_index = 0
            self.anim_timer = 0

        if self.direction == 'up':
            self.image = self.up_frames[self.anim_index % len(self.up_frames)]
        elif self.direction == 'down':
            self.image = self.down_frames[self.anim_index % len(self.down_frames)]
        elif self.direction == 'left':
            self.image = self.walk_frames_left[self.anim_index % len(self.walk_frames_left)]
        else:
            self.image = self.walk_frames_right[self.anim_index % len(self.walk_frames_right)]

        # 6) déplacement normal
        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH  - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))

    def can_attack(self):
        return self.attack_timer >= self.attack_cooldown

    def attack(self, enemies, mouse_pos):
        if not self.can_attack():
            return
        # joue le son et initialise visuel & cooldown
        self.attack_sound.play()
        self.attacking           = True
        self.attack_timer        = 0
        self.attack_timer_visual = self.attack_duration

        # calcule l’angle de l’attaque
        dxm = mouse_pos[0] - self.rect.centerx
        dym = mouse_pos[1] - self.rect.centery
        angle = math.degrees(math.atan2(-dym, dxm)) % 360
        self.last_attack_angle = angle

        half = self.attack_angle / 2
        for e in enemies:
            # vecteur joueur→ennemi
            dxe = e.rect.centerx - self.rect.centerx
            dye = e.rect.centery  - self.rect.centery
            dist = math.hypot(dxe, dye)
            r = e.rect.width / 2
            # si dans la portée
            if dist - r <= self.attack_range:
                # calcule l’angle joueur→ennemi
                a2e = math.degrees(math.atan2(-dye, dxe)) % 360
                delta = abs((angle - a2e + 180) % 360 - 180)
                if delta <= half:
                    # si l’ennemi implémente take_damage(), on l’appelle
                    if hasattr(e, "take_damage"):
                        e.take_damage(self.attack_damage)
                    else:
                        # sinon on retire directement les PV et on déclenche le flash
                        e.hp -= self.attack_damage
                        e.flash_timer = getattr(e, "flash_duration", 0)

    def scream(self, normal_enemies, mages, mouse_pos):
        """Cri en cône de 45° vers la souris : slow + dégâts."""
        if self.scream_timer > 0:
            return
        # son & cooldown
        self.scream_sound.play()
        self.scream_timer = self.scream_cooldown
        # afficher cône
        self.show_scream_cone   = True
        self.scream_cone_timer  = 0.3

        # calcule angle vers la souris
        dxm = mouse_pos[0] - self.rect.centerx
        dym = mouse_pos[1] - self.rect.centery
        center_angle = math.degrees(math.atan2(-dym, dxm)) % 360
        self.scream_angle = center_angle
        half_cone = 45 / 2

        for e in normal_enemies + mages:
            dx = e.rect.centerx - self.rect.centerx
            dy = e.rect.centery  - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > self.scream_range:
                continue
            angle_to_enemy = math.degrees(math.atan2(-dy, dx)) % 360
            delta = abs((center_angle - angle_to_enemy + 180) % 360 - 180)
            if delta <= half_cone:
                e.hp -= self.scream_damage
                e.slow_timer = self.scream_slow_duration

    def take_damage(self, amount):
        """Gère la prise de dégâts : on consomme d’abord l’armure, puis les PV."""
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

        self.next_level_xp = int(self.next_level_xp * 1.18)
        self.new_level     = True
        self.levelup_sound.play()
        self.armor         = self.max_arm
        self.attack_damage += 1.2

    # pool d’améliorations
    UPGRADE_KEYS = [
        "Strength Boost", "Vitality Surge", "Quick Reflexes",
        "Haste", "Armor Plating", "Extended Reach", "XP Bonus"
    ]
    UPGRADE_INFO = {
        "Strength Boost":   {"type":"flat",   "value": 2.5,  "unit":"Damage"},
        "Vitality Surge":   {"type":"flat",   "value": 5,    "unit":"Max HP"},
        "Quick Reflexes":   {"type":"mult",   "value": 0.85,  "unit":"Cooldown"},
        "Haste":            {"type":"flat",   "value": 30,  "unit":"Speed"},
        "Armor Plating":    {"type":"flat",   "value": 5,    "unit":"Armor"},
        "Extended Reach":   {"type":"flat",   "value":20,    "unit":"Range"},
        "XP Bonus":         {"type":"percent","value": 0.20, "unit":"XP"}
    }

    def apply_upgrade(self, key):
        if key == "Strength Boost":
            self.attack_damage += 3
        elif key == "Vitality Surge":
            self.max_hp += 5
            self.hp     += 5
        elif key == "Quick Reflexes":
            self.attack_cooldown *= 0.85
        elif key == "Haste":
            self.speed += 30
        elif key == "Armor Plating":
            self.max_arm += 5
            self.armor   += 5
        elif key == "Extended Reach":
            self.attack_range += 20
        elif key == "XP Bonus":
            self.xp_bonus += 0.20


    def apply_bonus(self, bonus_type):
        """Applique un bonus au joueur."""
        if bonus_type == "magnet":
            self.magnet_active = True
            self.magnet_timer  = self.magnet_duration

    def draw(self, surface, cam_x, cam_y):
        # 1) afficher cône
        if self.show_scream_cone:
            cone_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
            apex_x = self.rect.centerx - cam_x
            apex_y = self.rect.centery  - cam_y
            half_cone = 45 / 2
            length    = self.scream_range
            angles = [self.scream_angle - half_cone, self.scream_angle + half_cone]
            points = [(apex_x, apex_y)]
            for a in angles:
                rad = math.radians(a)
                x = apex_x + math.cos(rad) * length
                y = apex_y - math.sin(rad) * length
                points.append((x, y))
            pygame.draw.polygon(cone_surf, (0,0,255,51), points)
            surface.blit(cone_surf, (0,0))

        # 2) dessiner joueur
        if   self.direction == 'up':    y_off = self.offset_up
        elif self.direction == 'down':  y_off = self.offset_down
        else:                           y_off = 0

        surface.blit(self.image, (self.rect.x - cam_x,
                                  self.rect.y - cam_y + y_off))

        # 3) slash si attaque
        if self.attacking:
            rot   = self.last_attack_angle - 225
            slash = pygame.transform.rotozoom(self.raw_slash, rot, self.slash_scale)
            sw, sh = slash.get_size()
            rad    = math.radians(self.last_attack_angle)
            dx_off = math.cos(rad) * (self.attack_range * 0.5)
            dy_off = -math.sin(rad) * (self.attack_range * 0.5)
            px     = self.rect.centerx + dx_off - sw//2 - cam_x
            py     = self.rect.centery  + dy_off - sh//2 - cam_y + y_off
            surface.blit(slash, (px, py))
