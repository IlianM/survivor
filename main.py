import pygame
import random
import math
import sys
import os
from settings import *
from player import Player
from enemy import Enemy
from xp_orb import XPOrb

class UpgradeMenu:
    def __init__(self):
        self.choices = []
        self.rects   = []
        self.font    = pygame.font.Font(None, 28)
        self.btn_w   = 240
        self.btn_h   = 120
        self.margin  = 40

    def open(self):
        self.choices = random.sample(Player.UPGRADE_KEYS, 3)
        self.rects.clear()
        total_w = 3 * self.btn_w + 2 * self.margin
        start_x = (WIDTH - total_w) // 2
        y = (HEIGHT - self.btn_h) // 2
        for i in range(3):
            r = pygame.Rect(
                start_x + i * (self.btn_w + self.margin),
                y,
                self.btn_w,
                self.btn_h
            )
            self.rects.append(r)

    def draw(self, surf, alpha=255):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, alpha//2))
        surf.blit(ov, (0, 0))
        for key, rect in zip(self.choices, self.rects):
            info = Player.UPGRADE_INFO[key]
            if info["type"] == "flat":
                desc = f"+{info['value']} {info['unit']}"
            elif info["type"] == "percent":
                pct = int(info["value"] * 100)
                desc = f"+{pct}% {info['unit']}"
            else:  # 'mult'
                pct = int((info["value"] - 1) * 100)
                sign = "+" if pct > 0 else ""
                desc = f"{sign}{pct}% {info['unit']}"

            pygame.draw.rect(surf, (50,50,50), rect)
            pygame.draw.rect(surf, (200,200,200), rect, 2)
            title = self.font.render(key, True, (255,255,255))
            surf.blit(title, (rect.x+10, rect.y+10))
            text  = self.font.render(desc, True, (200,200,200))
            surf.blit(text,  (rect.x+10, rect.y+40))

pygame.init()
pygame.mixer.init()
BACKGROUND_MUSIC = os.path.join("fx", "background_music.mp3")
music_volume     = 0.5   # ajuste entre 0.0 et 1.0
pygame.mixer.music.load(BACKGROUND_MUSIC)
pygame.mixer.music.set_volume(music_volume)
pygame.mixer.music.play(-1, fade_ms=2000)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Death Must Pygame")
clock = pygame.time.Clock()

bg_img = pygame.image.load("assets/background.png").convert()
bg_w, bg_h = bg_img.get_size()

player      = Player(MAP_WIDTH//2, MAP_HEIGHT//2)
enemy_list  = []
xp_orbs     = []
spawn_timer = 0.0
base_spawn_interval = 3  # seconds

font_menu    = pygame.font.Font(None, 64)
start_button = pygame.Rect(WIDTH//2-100, HEIGHT//2-25, 200, 50)
main_menu    = True

game_over    = False
kills        = 0
survival_time= 0
start_ticks  = pygame.time.get_ticks()

upgrade_menu   = UpgradeMenu()
upgrade_active = False
upgrade_fade   = 0.0
fade_in_dur    = 0.5
fade_out_dur   = 1.0

def draw_tiled_background(surf, cx, cy):
    ox = -(cx % bg_w)
    oy = -(cy % bg_h)
    y = oy - bg_h
    while y < HEIGHT:
        x = ox - bg_w
        while x < WIDTH:
            surf.blit(bg_img, (x, y))
            x += bg_w
        y += bg_h

running = True
while running:
    dt = clock.tick(FPS) / 1000

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Start game
        if main_menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if start_button.collidepoint(event.pos):
                main_menu   = False
                start_ticks = pygame.time.get_ticks()
                kills       = 0
                game_over   = False
                enemy_list.clear()
                xp_orbs.clear()
                player.__init__(MAP_WIDTH//2, MAP_HEIGHT//2)

        # Toggle Y auto-attack
        if (event.type == pygame.KEYDOWN and not main_menu
                and not upgrade_active and not game_over):
            if event.key == pygame.K_y:
                player.auto_attack = not player.auto_attack
            elif event.key == pygame.K_k:
                upgrade_active = not upgrade_active
                upgrade_fade   = 0.0 if upgrade_active else fade_out_dur

        # Click in upgrade menu
        if upgrade_active and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for key, rect in zip(upgrade_menu.choices, upgrade_menu.rects):
                if rect.collidepoint(mx, my):
                    player.apply_upgrade(key)
                    player.new_level = False
                    upgrade_active   = False
                    upgrade_fade     = 0.0  # disappear immediately
                    break

    # Main menu
    if main_menu:
        screen.fill((0,0,0))
        pygame.draw.rect(screen, (0,200,0), start_button)
        txt = font_menu.render("Start Game", True, (255,255,255))
        screen.blit(txt, (
            start_button.x + (200 - txt.get_width())//2,
            start_button.y + (50  - txt.get_height())//2
        ))
        pygame.display.flip()
        continue

    # Auto‐open on level up
    if player.new_level and not upgrade_active:
        upgrade_menu.open()
        upgrade_active = True
        upgrade_fade   = 0.0

    # Camera
    cam_x = max(0, min(player.rect.centerx - WIDTH//2, MAP_WIDTH - WIDTH))
    cam_y = max(0, min(player.rect.centery - HEIGHT//2, MAP_HEIGHT - HEIGHT))

    # Game update
    if not upgrade_active and not main_menu and not game_over:
        keys = pygame.key.get_pressed()
        player.update(keys, dt)

        # Attacks
        if player.auto_attack and enemy_list:
            tgt = min(enemy_list, key=lambda e: math.hypot(
                e.rect.centerx-player.rect.centerx,
                e.rect.centery-player.rect.centery
            ))
            player.attack(enemy_list, tgt.rect.center)
        elif pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            player.attack(enemy_list, (mx+cam_x, my+cam_y))

        # Spawn logic with dynamic elite/rare rates
        game_time     = (pygame.time.get_ticks() - start_ticks) / 1000
        elite_chance  = min(0.1, player.level * 0.005)
        rare_chance   = min(0.3, player.level * 0.015)
        time_mod      = 1 + game_time / 60
        level_mod     = max(0.2, 1 - player.level * 0.01)
        spawn_interval= max(0.05, base_spawn_interval * level_mod / time_mod)

        spawn_timer += dt
        if spawn_timer >= spawn_interval:
            spawn_timer = 0.0
            margin = 50
            edge   = random.choice(['top','bottom','left','right'])
            if edge == 'top':
                x = random.randint(int(cam_x), int(cam_x+WIDTH));   y = cam_y - margin
            elif edge == 'bottom':
                x = random.randint(int(cam_x), int(cam_x+WIDTH));   y = cam_y + HEIGHT + margin
            elif edge == 'left':
                x = cam_x - margin;                                y = random.randint(int(cam_y), int(cam_y+HEIGHT))
            else:
                x = cam_x + WIDTH + margin;                        y = random.randint(int(cam_y), int(cam_y+HEIGHT))

            r = random.random()
            if   r < elite_chance:
                tier = 'elite'
            elif r < elite_chance + rare_chance:
                tier = 'rare'
            else:
                tier = 'normal'

            enemy_list.append(Enemy(x, y, speed=60, tier=tier, player_level=player.level))

        # 1) Update enemies
        for e in enemy_list:
            e.update(player.rect.center, dt)

        # 2) Separation
        for i in range(len(enemy_list)):
            e1 = enemy_list[i]
            for j in range(i+1, len(enemy_list)):
                e2 = enemy_list[j]
                dx = e1.rect.centerx - e2.rect.centerx
                dy = e1.rect.centery   - e2.rect.centery
                dist = math.hypot(dx, dy)
                min_dist = (e1.rect.width + e2.rect.width) * 0.5
                if 0 < dist < min_dist:
                    overlap = min_dist - dist
                    nx, ny   = dx / dist, dy / dist
                    shift_x  = nx * overlap * 0.5
                    shift_y  = ny * overlap * 0.5
                    e1.rect.x += shift_x; e1.rect.y += shift_y
                    e2.rect.x -= shift_x; e2.rect.y -= shift_y

        # 3) Collisions, death & cleanup
        for e in enemy_list[:]:
            hb = player.rect.inflate(-100, -100)
            if e.rect.colliderect(hb):
                if e.attack_timer <= 0:
                    player.take_damage(e.damage)
                    e.attack_timer = e.attack_cooldown
                    e.pause_timer  = 0.5
                continue
            if e.hp <= 0:
                kills += 1
                xp_orbs.append(XPOrb(e.rect.centerx, e.rect.centery, e.xp_value))
                enemy_list.remove(e)
                continue
            dx = e.rect.centerx - player.rect.centerx
            dy = e.rect.centery - player.rect.centery
            if math.hypot(dx, dy) > max(WIDTH, HEIGHT) * 2:
                enemy_list.remove(e)

        # XP orbs update & pickup
        for orb in xp_orbs:
            orb.update(dt, player.rect.center)
        for orb in xp_orbs[:]:
            if orb.rect.colliderect(player.rect):
                # jouer le son de ramassage
                orb.pickup_sound.play()
                player.gain_xp(orb.value)
                xp_orbs.remove(orb)
        # Game over?
        if player.hp <= 0:
            game_over     = True
            survival_time = game_time

    # Drawing
    draw_tiled_background(screen, cam_x, cam_y)
    for orb in xp_orbs: orb.draw(screen, cam_x, cam_y)
    for e in enemy_list:
        e.draw(screen, cam_x, cam_y)
        ex, ey = e.rect.x - cam_x, e.rect.y - cam_y
        bw, bh = e.rect.width, 5
        pygame.draw.rect(screen, (100,0,0), (ex, ey-bh-2, bw, bh))
        pygame.draw.rect(screen, (0,200,0), (ex, ey-bh-2, bw*(e.hp/e.max_hp), bh))
    player.draw(screen, cam_x, cam_y)

    # HUD
    abw, abh = 300,20; ax, ay = 20,20
    pygame.draw.rect(screen, (50,50,50), (ax,ay,abw,abh))
    pr = max(player.armor,0)/player.max_arm
    pygame.draw.rect(screen, (0,150,150), (ax,ay,abw*pr,abh))
    pygame.draw.rect(screen, (255,255,255), (ax,ay,abw,abh),2)

    hy = ay+abh+5
    pygame.draw.rect(screen, (100,0,0), (ax,hy,abw,abh))
    hr = max(player.hp,0)/player.max_hp
    pygame.draw.rect(screen, (0,200,0), (ax,hy,abw*hr,abh))
    pygame.draw.rect(screen, (255,255,255), (ax,hy,abw,abh),2)

    xy = hy+abh+5
    pygame.draw.rect(screen, (80,80,0), (ax,xy,abw,10))
    xr = player.xp/player.next_level_xp
    pygame.draw.rect(screen, (200,200,0), (ax,xy,abw*xr,10))
    pygame.draw.rect(screen, (255,255,255), (ax,xy,abw,10),1)

    font = pygame.font.Font(None,24)
    screen.blit(font.render(f"Level: {player.level}",True,(255,255,255)),(ax,xy+15))
    screen.blit(font.render(f"SP: {player.skill_points}",True,(255,255,255)),(ax+150,xy+15))

    # Game Over
    if game_over:
        screen.fill((0,0,0))
        f1 = pygame.font.Font(None,72)
        f2 = pygame.font.Font(None,48)
        lines = [
            "GAME OVER",
            f"Survived: {survival_time:.1f}s",
            f"Level:    {player.level}",
            f"Monster exterminated:    {kills}"
        ]
        for i, text in enumerate(lines):
            font_ = f1 if i==0 else f2
            surf  = font_.render(text,True,(255,255,255))
            screen.blit(surf, ((WIDTH - surf.get_width())//2,150+i*80))

    # Upgrade menu fade
    if upgrade_active or (not player.new_level and upgrade_fade>0):
        if upgrade_active:
            upgrade_fade = min(upgrade_fade + dt, fade_in_dur)
        else:
            upgrade_fade = max(upgrade_fade - dt, 0)
        alpha = int(255 * (upgrade_fade/fade_in_dur))
        upgrade_menu.draw(screen, alpha)

    pygame.display.flip()
