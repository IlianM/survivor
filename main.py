import pygame
import random
import math
import sys
from settings import *
from player import Player
from enemy import Enemy

# Classe pour le menu des compétences
class SkillMenu:
    def __init__(self, player):
        self.player = player
        self.branches = list(player.skill_tree.keys())
        self.options = []  # tuples (branche, compétence, rect)
        self.font = pygame.font.Font(None, 28)
        self.margin = 50
        self.btn_w = 200
        self.btn_h = 40
        self.build_buttons()

    def build_buttons(self):
        self.options.clear()
        start_x = self.margin
        start_y = self.margin + 80
        for i, branch in enumerate(self.branches):
            bx = start_x + i * (self.btn_w + self.margin)
            for j, skill in enumerate(self.player.skill_tree[branch]):
                rect = pygame.Rect(bx, start_y + j * (self.btn_h + 10), self.btn_w, self.btn_h)
                self.options.append((branch, skill, rect))

    def draw(self, surface):
        # Overlay semi-transparent
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        surface.blit(ov, (0, 0))

        # Titre
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("Skill Tree", True, (255, 255, 255))
        surface.blit(title, ((WIDTH - title.get_width()) // 2, 20))

        # Points de compétence restants
        sp_txt = self.font.render(f"Skill Points: {self.player.skill_points}", True, (255, 255, 0))
        surface.blit(sp_txt, (20, 80))

        # Titres des branches
        for i, branch in enumerate(self.branches):
            bx = self.margin + i * (self.btn_w + self.margin)
            btitle = self.font.render(branch.capitalize(), True, (200, 200, 200))
            surface.blit(btitle, (bx, self.margin))

        # Boutons de compétence
        for branch, skill, rect in self.options:
            unlocked = self.player.skill_tree[branch][skill]
            if unlocked:
                clr = (100, 100, 100)
            elif self.player.skill_points > 0:
                clr = (0, 200, 0)
            else:
                clr = (150, 150, 150)
            pygame.draw.rect(surface, clr, rect)
            txt = self.font.render(skill, True, (255, 255, 255))
            surface.blit(txt, (rect.x + 5, rect.y + 5))


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Death Must Pygame")
clock = pygame.time.Clock()

# Charger et tuiler le background
bg_img = pygame.image.load("assets/background.png").convert()
bg_w, bg_h = bg_img.get_size()

# Police et bouton du menu principal
font_menu = pygame.font.Font(None, 64)
start_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)

# Entités et timers
player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
enemy_list = []
spawn_timer = 0
SPAWN_INTERVAL = 0.2

# États des menus
main_menu = True
menu_active = False
menu = SkillMenu(player)

# Tracking
start_ticks = pygame.time.get_ticks()
kills = 0

def draw_tiled_background(surface, cam_x, cam_y):
    offset_x = -(cam_x % bg_w)
    offset_y = -(cam_y % bg_h)
    y = offset_y - bg_h
    while y < HEIGHT:
        x = offset_x - bg_w
        while x < WIDTH:
            surface.blit(bg_img, (x, y))
            x += bg_w
        y += bg_h

running = True
game_over = False
survival_time = 0

while running:
    dt = clock.tick(FPS) / 1000

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if main_menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_button.collidepoint(event.pos):
                main_menu = False
                # réinitialiser timer et kills
                start_ticks = pygame.time.get_ticks()
                kills = 0
        if not main_menu:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    menu_active = not menu_active
                elif event.key == pygame.K_y:
                    player.auto_attack = not player.auto_attack
            if menu_active and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # …

                mx, my = event.pos
                for branch, skill, rect in menu.options:
                    if rect.collidepoint(mx, my):
                        if player.spend_skill(branch, skill):
                            menu.build_buttons()

    # Menu principal
    if main_menu:
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, (0, 200, 0), start_button)
        txt = font_menu.render("Start Game", True, (255, 255, 255))
        screen.blit(txt, (start_button.x + (start_button.w - txt.get_width()) // 2,
                          start_button.y + (start_button.h - txt.get_height()) // 2))
        pygame.display.flip()
        continue

    # Calcul de la caméra
    cam_x = max(0, min(player.rect.centerx - WIDTH // 2, MAP_WIDTH - WIDTH))
    cam_y = max(0, min(player.rect.centery - HEIGHT // 2, MAP_HEIGHT - HEIGHT))

    # Mise à jour du jeu si pas en skill menu et pas game over
    if not menu_active and not game_over:
        # Mise à jour du joueur
        keys = pygame.key.get_pressed()
        player.update(keys, dt)


        if player.auto_attack and enemy_list:
            # Trouver l'ennemi le plus proche
            closest = min(enemy_list,
                        key=lambda e: math.hypot(
            e.rect.centerx - player.rect.centerx,
            e.rect.centery - player.rect.centery))
            # Viser son centre
            target_pos = closest.rect.center
            player.attack(enemy_list, target_pos)

        # Attaque
        elif pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            virt_mouse = (mx + cam_x, my + cam_y)
            player.attack(enemy_list, virt_mouse)

        # Spawn d'ennemis
        spawn_timer += dt
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0
            edge = random.choice(["top", "bottom", "left", "right"])
            if edge == "top":
                x, y = random.randint(0, MAP_WIDTH), -30
            elif edge == "bottom":
                x, y = random.randint(0, MAP_WIDTH), MAP_HEIGHT + 30
            elif edge == "left":
                x, y = -30, random.randint(0, MAP_HEIGHT)
            else:
                x, y = MAP_WIDTH + 30, random.randint(0, MAP_HEIGHT)
            enemy_list.append(Enemy(x, y))

        # Mise à jour des ennemis & collisions
# Mise à jour des ennemis & collisions
        for enemy in enemy_list[:]:
            enemy.update(player.rect.center, dt)
            hitbox = player.rect.inflate(-100, -100)
            if enemy.rect.colliderect(hitbox):
                player.take_damage(enemy.damage)
                enemy_list.remove(enemy)
                continue
            if enemy.hp <= 0:
                kills += 1
                player.gain_xp(enemy.xp_value)
                enemy_list.remove(enemy)

        # Vérifier défaite
        if player.hp <= 0:
            game_over = True
            survival_time = (pygame.time.get_ticks() - start_ticks) / 1000

    # Dessin du monde ou du game over
    if not game_over:
        # Dessin du background et des entités
        draw_tiled_background(screen, cam_x, cam_y)
        for enemy in enemy_list:
            ex = enemy.rect.x - cam_x
            ey = enemy.rect.y - cam_y
            screen.blit(enemy.image, (ex, ey))
            # Petite barre de vie des ennemis
            bw = enemy.rect.width
            bh = 5
            bar_x = ex
            bar_y = ey - bh - 2
            pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bw, bh))
            health_ratio = enemy.hp / enemy.max_hp
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, bw * health_ratio, bh))

        # Dessin du joueur
        player.draw(screen, cam_x, cam_y)

        if player.auto_attack:
            ico = pygame.font.Font(None, 30).render("⚔ AUTO", True, (255,200,0))
            screen.blit(ico, (WIDTH-100, 10))


        # HUD existant (armure, vie, XP, level, skill points)
        # Barre d’armure
        armor_bar_w = 300
        armor_bar_h = 20
        ax, ay = 20, 20
        pygame.draw.rect(screen, (50, 50, 50), (ax, ay, armor_bar_w, armor_bar_h))
        armor_ratio = max(player.armor, 0) / player.max_arm
        pygame.draw.rect(screen, (0, 150, 150), (ax, ay, armor_bar_w * armor_ratio, armor_bar_h))
        pygame.draw.rect(screen, (255, 255, 255), (ax, ay, armor_bar_w, armor_bar_h), 2)

        # Barre de vie
        hp_bar_h = 20
        hy = ay + armor_bar_h + 5
        pygame.draw.rect(screen, (100, 0, 0), (ax, hy, armor_bar_w, hp_bar_h))
        hp_ratio = max(player.hp, 0) / player.max_hp
        pygame.draw.rect(screen, (0, 200, 0), (ax, hy, armor_bar_w * hp_ratio, hp_bar_h))
        pygame.draw.rect(screen, (255, 255, 255), (ax, hy, armor_bar_w, hp_bar_h), 2)

        # Barre d’XP
        xp_bar_h = 10
        xy = hy + hp_bar_h + 5
        pygame.draw.rect(screen, (80, 80, 0), (ax, xy, armor_bar_w, xp_bar_h))
        xp_ratio = player.xp / player.next_level_xp
        pygame.draw.rect(screen, (200, 200, 0), (ax, xy, armor_bar_w * xp_ratio, xp_bar_h))
        pygame.draw.rect(screen, (255, 255, 255), (ax, xy, armor_bar_w, xp_bar_h), 1)

        # Level & Skill Points
        font = pygame.font.Font(None, 24)
        txt_level = font.render(f"Level: {player.level}", True, (255, 255, 255))
        screen.blit(txt_level, (ax, xy + xp_bar_h + 5))
        txt_sp = font.render(f"Skill Points: {player.skill_points}", True, (255, 255, 255))
        screen.blit(txt_sp, (ax + 150, xy + xp_bar_h + 5))

        # Affichage du menu de compétences si actif
        if menu_active:
            menu.draw(screen)

    else:
        # Écran Game Over
        screen.fill((0, 0, 0))
        f1 = pygame.font.Font(None, 72)
        f2 = pygame.font.Font(None, 48)
        lines = [
            "GAME OVER",
            f"Survived: {survival_time:.1f} s",
            f"Level:    {player.level}",
            f"Kills:    {kills}"
        ]
        for i, text in enumerate(lines):
            font = f1 if i == 0 else f2
            surf = font.render(text, True, (255, 255, 255))
            screen.blit(surf, ((WIDTH - surf.get_width()) // 2, 150 + i * 80))

    pygame.display.flip()

pygame.quit()
