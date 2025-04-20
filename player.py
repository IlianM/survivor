import pygame
import math
import os
from settings import MAP_WIDTH, MAP_HEIGHT

class Player:
    def __init__(self, x, y):
        # Charger les sprites droite (2 frames) et gauche (miroir)
        base = os.path.join("assets", "knight")
        self.walk_frames_right = [
            pygame.transform.scale(
                pygame.image.load(base + "-right.png").convert_alpha(),
                (96, 96)
            ),
            pygame.transform.scale(
                pygame.image.load(base + "2-right.png").convert_alpha(),
                (96, 96)
            )
        ]
        self.walk_frames_left = [pygame.transform.flip(f, True, False)
                                 for f in self.walk_frames_right]

        # Frame de repos
        self.image = self.walk_frames_right[0]
        self.rect  = self.image.get_rect(center=(x, y))

        # Animation marche
        self.anim_index    = 0
        self.anim_timer    = 0.0
        self.anim_interval = 0.2

        # Mouvement
        self.speed = 200

        # PV et armure
        self.max_hp  = 10
        self.hp      = self.max_hp
        self.max_arm = 5
        self.armor   = self.max_arm

        # Attaque
        self.attack_range     = 120
        self.attack_cooldown  = 0.5
        self.attack_timer     = 0.0
        self.attack_angle     = 90
        self.attack_damage    = 1
        self.attacking        = False
        self.attack_duration  = 0.2
        self.attack_timer_visual = 0.0

        # XP & progression
        self.xp            = 0
        self.level         = 1
        self.next_level_xp = 20
        self.skill_points  = 0
        self.skill_tree    = {
            'warrior': {'Unlock Spin Attack': False, 'Unlock Dash': False},
            'paladin': {'Unlock Shield Bash': False, 'Unlock Heal': False},
            'thief': {'Unlock Backstab': False, 'Unlock Evasion': False},
        }

        self.auto_attack = False
        self.last_attack_angle = 0
    def update(self, keys, dt):
        # — Détection input —
        dx = dy = 0
        if keys[pygame.K_z]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_q]: dx -= 1
        if keys[pygame.K_d]: dx += 1

        # — Animation marche —
        if dx != 0:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_interval:
                self.anim_timer -= self.anim_interval
                self.anim_index = (self.anim_index + 1) % len(self.walk_frames_right)
        else:
            self.anim_index = 0
            self.anim_timer = 0

        # — Choix du sprite selon direction —
        if dx < 0:
            self.image = self.walk_frames_left[self.anim_index]
        elif dx > 0:
            self.image = self.walk_frames_right[self.anim_index]
        # si dx == 0, on garde l’image courante

        # — Déplacement —
        self.rect.x += dx * self.speed * dt
        self.rect.y += dy * self.speed * dt

        # — Murs invisibles —
        self.rect.x = max(0, min(self.rect.x, MAP_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, MAP_HEIGHT - self.rect.height))

        # — Timers attaque —
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
        # -- calculer l'angle vers la cible une seule fois --
        dxm = mouse_pos[0] - self.rect.centerx
        dym = mouse_pos[1] - self.rect.centery
        angle_to_mouse = math.degrees(math.atan2(-dym, dxm)) % 360
        self.last_attack_angle = angle_to_mouse

        self.attack_timer = 0
        self.attacking = True
        self.attack_timer_visual = self.attack_duration

        # ... reste de ton code qui inflige les dégâts ...

        # Calcul angle visée
        dxm = mouse_pos[0] - self.rect.centerx
        dym = mouse_pos[1] - self.rect.centery
        angle_to_mouse = math.degrees(math.atan2(-dym, dxm)) % 360
        half_cone = self.attack_angle / 2

        # Infliger des dégats, mais ne retire plus l’ennemi ni ne donne d’XP
        for enemy in enemies:
            dxe = enemy.rect.centerx - self.rect.centerx
            dye = enemy.rect.centery - self.rect.centery
            dist = math.hypot(dxe, dye)
            r = enemy.rect.width / 2
            if dist - r <= self.attack_range:
                angle_to_enemy = math.degrees(math.atan2(-dye, dxe)) % 360
                delta = abs((angle_to_mouse - angle_to_enemy + 180) % 360 - 180)
                if delta <= half_cone:
                    enemy.hp -= self.attack_damage

    def take_damage(self, amount):
        if self.armor > 0:
            self.armor -= 1
        else:
            self.hp -= amount

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= self.next_level_xp:
            self.xp -= self.next_level_xp
            self.level_up()

    def level_up(self):
        self.level += 1
        self.skill_points += 1
        self.next_level_xp = int(self.next_level_xp * 1.5)

        # Bonus automatiques
        self.max_hp += 2
        self.hp = self.max_hp
        self.max_arm += 1
        self.armor = self.max_arm
        self.attack_damage += 0.2
        self.speed += 5

    def spend_skill(self, branch, skill):
        if self.skill_points <= 0 or branch not in self.skill_tree or self.skill_tree[branch][skill]:
            return False
        self.skill_points -= 1
        self.skill_tree[branch][skill] = True
        # Appliquer le bonus...
        return True

    def draw(self, surface, cam_x, cam_y):
        surface.blit(self.image, (self.rect.x - cam_x, self.rect.y - cam_y))
        if self.attacking:
            half_cone = self.attack_angle / 2
            surf = pygame.Surface((self.attack_range*2, self.attack_range*2), pygame.SRCALPHA)
            # on n'utilise plus pygame.mouse.get_pos(), mais l'angle stocké
            ang = self.last_attack_angle
            pygame.draw.arc(
                surf,
                (255, 255, 0, 100),
                surf.get_rect(),
                math.radians(ang - half_cone),
                math.radians(ang + half_cone),
                20
            )
            surface.blit(
                surf,
                (self.rect.centerx - self.attack_range - cam_x,
                self.rect.centery - self.attack_range - cam_y)
            )
