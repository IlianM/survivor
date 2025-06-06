import pygame
import pygame.gfxdraw
import random
import math
import sys
import os
import pygame.surfarray as surfarray
import numpy as np

from .settings import *
from .player import Player
from .enemy import Enemy
from .xp_orb import XPOrb
from .goblin_mage import GoblinMage
from .boss import Boss
from PIL import Image
from .utils import resource_path

from .settings import WIDTH, HEIGHT   # ou votre constante de chemin

# — Globals that must be loaded after pygame.display is ready —
ICON_SIZE       = 64
CRI_ICON_PATH   = os.path.join("assets", "cri.png")
CRI_ICON        = None
CRI_ICON_GRAY   = None
FONT_SMALL      = None

HEALTH_ORNAMENT = None
HEALTH_TEXTURE  = None

# Cap de monstres, évolue avec le level
BASE_MAX_ENEMIES   = 5   # mobs minimum level 1
PER_LEVEL_ENEMIES  = 2   # mobs en plus par level

TOUCHES_IMG_PATH = os.path.join("assets", "touches.png")


def get_cri_icons():
    """Lazy-load color + grayscale CRI_ICON and small font."""
    global CRI_ICON, CRI_ICON_GRAY, FONT_SMALL
    if CRI_ICON is None:
        # 1) Load & scale the color icon
        raw = pygame.image.load(resource_path(CRI_ICON_PATH)).convert_alpha()
        CRI_ICON = pygame.transform.scale(raw, (ICON_SIZE, ICON_SIZE))
        # 2) Build grayscale version
        CRI_ICON_GRAY = pygame.Surface((ICON_SIZE, ICON_SIZE), pygame.SRCALPHA)
        CRI_ICON_GRAY.blit(CRI_ICON, (0, 0))
        arr = surfarray.array3d(CRI_ICON_GRAY)
        lum = (
            0.299 * arr[:, :, 0] +
            0.587 * arr[:, :, 1] +
            0.114 * arr[:, :, 2]
        ).astype("uint8")
        gray_arr = np.stack([lum, lum, lum], axis=2)
        surfarray.blit_array(CRI_ICON_GRAY, gray_arr)
        # 3) Load a small Font for cooldown text
        FONT_SMALL = pygame.font.Font(
            resource_path("assets/fonts/Cinzel/static/Cinzel-Regular.ttf"),
            20
        )
    return CRI_ICON, CRI_ICON_GRAY, FONT_SMALL


def draw_tiled_background(surf, cx, cy, bg_img, bg_w, bg_h):
    ox = -(cx % bg_w)
    oy = -(cy % bg_h)
    y = oy - bg_h
    while y < HEIGHT:
        x = ox - bg_w
        while x < WIDTH:
            surf.blit(bg_img, (x, y))
            x += bg_w
        y += bg_h


class UpgradeMenu:
    def __init__(self):
        self.choices  = []
        self.rects    = []
        self.card_img = pygame.image.load(resource_path("assets/upgrade_card.png")).convert_alpha()
        self.btn_w, self.btn_h = self.card_img.get_size()
        self.margin        = 20
        self.font_title = pygame.freetype.Font(
            resource_path("assets/fonts/Cinzel/static/Cinzel-Regular.ttf"),
            24
        )
        self.font_body = pygame.freetype.Font(
            resource_path("assets/fonts/Cinzel/static/Cinzel-Regular.ttf"),
            16
        )

    def open(self):
        self.choices = random.sample(Player.UPGRADE_KEYS, 3)
        self.rects.clear()
        n = len(self.choices)
        group_w    = n * self.btn_w + (n - 1) * self.margin
        start_x    = (WIDTH - group_w) // 2
        y          = (HEIGHT - self.btn_h) // 2
        for i, key in enumerate(self.choices):
            x = start_x + i * (self.btn_w + self.margin)
            self.rects.append(pygame.Rect(x, y, self.btn_w, self.btn_h))

    def draw(self, surf, alpha=255, show_choices=True):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, alpha//2))
        surf.blit(ov, (0, 0))
        if not show_choices:
            return
        for key, rect in zip(self.choices, self.rects):
            surf.blit(self.card_img, rect.topleft)
            t_surf, t_rect = self.font_title.render(key, fgcolor=(255,255,255))
            t_rect.center  = (rect.centerx, rect.centery - 30)
            surf.blit(t_surf, t_rect)

            info = Player.UPGRADE_INFO[key]
            if info["type"] == "flat":
                desc = f"+{info['value']} {info['unit']}"
            elif info["type"] == "percent":
                desc = f"+{int(info['value']*100)}% {info['unit']}"
            else:
                pct  = int((info["value"] - 1) * 100)
                sign = "+" if pct > 0 else ""
                desc = f"{sign}{pct}% {info['unit']}"

            d_surf, d_rect = self.font_body.render(desc, fgcolor=(200,200,200))
            d_rect.center  = (rect.centerx, rect.centery + 30)
            surf.blit(d_surf, d_rect)


def draw_bottom_overlay(surface, overlay, y_offset=0, zoom=1):
    if zoom != 1.0:
        ov = pygame.transform.rotozoom(overlay, 0, zoom)
    else:
        ov = overlay
    rect = ov.get_rect()
    rect.midbottom = (WIDTH // 2, HEIGHT + y_offset)
    surface.blit(ov, rect)


def draw_health_globe(surface, cx, cy, radius, hp_ratio,
                      bg_color=(0,0,0,128), fg_color=(149,26,26),
                      outline_color=(255,255,255), outline_width=2):
    diameter = radius * 2
    pygame.gfxdraw.filled_circle(surface, cx, cy, radius, bg_color)
    if hp_ratio > 0:
        level_y = cy + radius - hp_ratio * diameter
        y_start = max(int(math.ceil(level_y)), cy - radius)
        y_end   = cy + radius
        texture = pygame.transform.smoothscale(HEALTH_TEXTURE, (diameter, diameter))
        mask    = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        for y in range(y_start, y_end + 1):
            dy      = y - cy
            dx      = int(math.sqrt(radius*radius - dy*dy))
            local_y = y - (cy - radius)
            local_x = (cx - dx) - (cx - radius)
            mask.fill((255,255,255,255), (local_x, local_y, dx*2, 1))
        masked = texture.copy()
        masked.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(masked, (cx - radius, cy - radius))
    pygame.draw.circle(surface, outline_color, (cx, cy), radius, outline_width)
    orn_size  = diameter + outline_width * 2 + 40
    ornament  = pygame.transform.smoothscale(HEALTH_ORNAMENT, (orn_size, orn_size))
    ornament  = pygame.transform.flip(ornament, True, False)
    orn_rect  = ornament.get_rect(center=(cx, cy))
    surface.blit(ornament, orn_rect)

def load_clean(path):
    """
    Try to pygame.load() and .convert_alpha(); if SDL_image balks,
    re-save via Pillow as 8-bit RGBA, load that, then delete temp.
    """
    try:
        return pygame.image.load(resource_path(path)).convert_alpha()

    except pygame.error:
        img = Image.open(path).convert("RGBA")
        tmp = path + ".clean.png"
        img.save(tmp)
        surf = pygame.image.load(resource_path(tmp)).convert_alpha()

        os.remove(tmp)
        return surf


def show_story_slideshow(screen, clock):
    """
    Play assets/story1.png … story7.png in sequence at 80% height:
     - Letterbox (black bars top/bottom)
     - FADE IN   (black→transparent)
     - HOLD 3s
     - FADE OUT  (transparent→black)
    Abort on any key/mouse (jumps straight out), QUIT closes.
    """
    sw, sh    = screen.get_size()
    target_h  = int(sh * 0.8)
    imgs      = []

    # Preload & scale each story frame
    for i in range(1, 8):
        path = os.path.join("assets", f"story{i}.png")
        raw  = load_clean(path)
        w    = int(target_h * raw.get_width() / raw.get_height())
        imgs.append(pygame.transform.smoothscale(raw, (w, target_h)))

    for img in imgs:
        rect  = img.get_rect(center=(sw//2, sh//2))
        black = pygame.Surface((sw, sh)); black.fill((0,0,0))
        skip  = False

        # FADE IN (alpha 255→0)
        for alpha in range(255, -1, -15):
            for e in pygame.event.get():
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                    if e.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    skip = True; break
            if skip: break

            black.set_alpha(alpha)
            screen.fill((0,0,0))
            screen.blit(img, rect)
            screen.blit(black, (0,0))
            pygame.display.flip()
            clock.tick(60)
        if skip: break

        # HOLD 3s (or until input)
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < 3000 and not skip:
            for e in pygame.event.get():
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                    if e.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    skip = True; break
            if skip: break
            screen.fill((0,0,0))
            screen.blit(img, rect)
            pygame.display.flip()
            clock.tick(30)
        if skip: break

        # FADE OUT (alpha 0→255)
        for alpha in range(0, 256, 15):
            for e in pygame.event.get():
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                    if e.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    skip = True; break
            if skip: break

            black.set_alpha(alpha)
            screen.fill((0,0,0))
            screen.blit(img, rect)
            screen.blit(black, (0,0))
            pygame.display.flip()
            clock.tick(60)
        if skip: break


def show_touches_screen(screen, clock):
    """
    Fade-in → wait for key/mouse → fade-out for TOUCHES_IMG,
    plus overlay the Cinzel key-binding text.
    """
    sw, sh  = screen.get_size()
    img     = load_clean(TOUCHES_IMG_PATH)
    img_rect= img.get_rect(center=(sw//2, sh//2))
    black   = pygame.Surface((sw, sh)); black.fill((0,0,0))

    # Prepare Cinzel text
    font_path = os.path.join("assets","fonts","Cinzel","static","Cinzel-Regular.ttf")
    font_size = 36
    font = pygame.font.Font(
        resource_path("assets/fonts/Cinzel/static/Cinzel-Regular.ttf"),
        font_size
    )
    lines     = ["Se déplacer : ZQSD", "Dash : ESPACE", "Cri : Clique droit"]
    spacing   = 10
    total_h   = len(lines)*font_size + (len(lines)-1)*spacing
    y_start   = sh//2 - total_h//2

    # FADE IN
    for alpha in range(255, -1, -5):
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                return
        black.set_alpha(alpha)
        screen.fill((0,0,0))
        screen.blit(img, img_rect)
        for i, txt in enumerate(lines):
            surf = font.render(txt, True, (255,255,255))
            r    = surf.get_rect(center=(sw//2,
                           y_start + i*(font_size+spacing) + font_size//2))
            screen.blit(surf, r)
        screen.blit(black, (0,0))
        pygame.display.flip()
        clock.tick(60)

    # WAIT for any key/mouse
    waiting = True
    while waiting:
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                waiting = False; break
        screen.fill((0,0,0))
        screen.blit(img, img_rect)
        for i, txt in enumerate(lines):
            surf = font.render(txt, True, (255,255,255))
            r    = surf.get_rect(center=(sw//2,
                           y_start + i*(font_size+spacing) + font_size//2))
            screen.blit(surf, r)
        pygame.display.flip()
        clock.tick(30)

    # FADE OUT
    for alpha in range(0, 256, 5):
        for e in pygame.event.get():
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                return
        black.set_alpha(alpha)
        screen.fill((0,0,0))
        screen.blit(img, img_rect)
        for i, txt in enumerate(lines):
            surf = font.render(txt, True, (255,255,255))
            r    = surf.get_rect(center=(sw//2,
                           y_start + i*(font_size+spacing) + font_size//2))
            screen.blit(surf, r)
        screen.blit(black, (0,0))
        pygame.display.flip()
        clock.tick(60)


# game/main.py
import pygame

def handle_scream_input(event, player, enemy_list, mages, cam_x, cam_y):
    """
    Gère un event pygame pour déclencher le cri :
    - si event est KEYDOWN et key == K_c, ou clic droit -> player.scream
    """
    if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
        mx, my = pygame.mouse.get_pos()
        player.scream(enemy_list, mages, (mx+cam_x, my+cam_y))
        return True
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
        mx, my = pygame.mouse.get_pos()
        player.scream(enemy_list, mages, (mx+cam_x, my+cam_y))
        return True
    return False


def draw_scream_cooldown(screen, player):
    """
    Display the scream icon centered horizontally,
    100px from the bottom, with a gray border while on cooldown,
    and a green border when ready.
    """
    icon, icon_gray, font_small = get_cri_icons()
    sw, sh   = screen.get_size()
    # position centrée :
    x        = sw // 2 - ICON_SIZE // 2
    y        = sh - 50 - ICON_SIZE

    # Choix de l'icône et de la couleur de bordure
    ready = (player.scream_timer <= 0)
    to_draw = icon if ready else icon_gray
    border_color = (0, 255, 0) if ready else (150, 150, 150)

    # Dessiner le contour avec la couleur appropriée
    border_rect = pygame.Rect(x - 2, y - 2, ICON_SIZE + 4, ICON_SIZE + 4)
    pygame.draw.rect(screen, border_color, border_rect, border_radius=4)

    # Afficher l’icône du cri
    screen.blit(to_draw, (x, y))

    # Si en cooldown, afficher le timer
    if not ready:
        text = f"{player.scream_timer:.1f}"
        surf = font_small.render(text, True, (255,255,255))
        rect = surf.get_rect(midbottom=(x + ICON_SIZE//2, y - 2))
        screen.blit(surf, rect)


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.freetype.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Reincarnation of the unkillable last human against all gods")

    # now that display is ready, you can safely call get_cri_icons() once
    get_cri_icons()

    # timers
    screen_flash_timer = 0.0
    FLASH_DURATION     = 0.08
    HIT_FLASH_DURATION = 0.05

    hit_flash_timer  = 0.0
    hit_flash_target = None

    global HEALTH_ORNAMENT, HEALTH_TEXTURE
    bottom_overlay   = pygame.image.load(resource_path("assets/bottom_overlay.png")).convert_alpha()
    HEALTH_ORNAMENT  = pygame.image.load(resource_path("assets/health_orb_ornement.png")).convert_alpha()
    HEALTH_TEXTURE   = pygame.image.load(resource_path("assets/health_texture.png")).convert_alpha()

    overlay_y_offset = 335
    overlay_zoom     = 0.9

    clock = pygame.time.Clock()
    pygame.mixer.music.load(resource_path("fx/background_music.mp3"))

    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, fade_ms=2000)

    main_menu       = True
    raw_menu = pygame.image.load(resource_path("assets/main_menu.png")).convert()

    main_menu_img   = pygame.transform.scale(raw_menu, (WIDTH, HEIGHT))
    play_button_rect= pygame.Rect(WIDTH//2 - 210, HEIGHT//2 + 50, 350, 120)

    BONUS_SIZE      = 64
    bg_img = pygame.image.load(resource_path("assets/background.png")).convert()

    bg_w, bg_h      = bg_img.get_size()
    magnet_raw = pygame.image.load(resource_path("assets/magnet.png")).convert_alpha()

    magnet_img      = pygame.transform.smoothscale(magnet_raw, (BONUS_SIZE, BONUS_SIZE))

    player     = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
    enemy_list = []
    mages      = []
    boss_list  = []
    xp_orbs    = []

    BONUS_TYPES = ["magnet"]
    OFFSET      = 200
    bonus_spawn_points = [
        (OFFSET, OFFSET),
        (MAP_WIDTH - BONUS_SIZE - OFFSET, OFFSET),
        (OFFSET, MAP_HEIGHT - BONUS_SIZE - OFFSET),
        (MAP_WIDTH - BONUS_SIZE - OFFSET, MAP_HEIGHT - BONUS_SIZE - OFFSET),
    ]
    current_bonus       = None

    spawn_timer         = 0.0
    base_spawn_interval = 3.0
    mage_spawn_chance   = 0.1
    start_ticks         = 0
    kills               = 0
    game_over           = False
    survival_time       = 0.0

    upgrade_menu         = UpgradeMenu()
    upgrade_active       = False
    upgrade_fade         = 0.0
    fade_in_dur          = 0.5
    fade_out_dur         = 1.0
    upgrade_resume_timer = 0.0


    while True:
        dt = clock.tick(FPS) / 1000
        screen_flash_timer = max(0.0, screen_flash_timer - dt)
        hit_flash_timer    = max(0.0, hit_flash_timer    - dt)


        hit_flash_timer = max(0.0, hit_flash_timer - dt)
        if hit_flash_timer == 0:
            hit_flash_target = None

        # Level up → menu + boss spawn
        if player.new_level:
            upgrade_menu.open()
            upgrade_active = True
            upgrade_fade   = 0.0
            if player.level % 10 == 0:
                safe_dist = 800
                while True:
                    bx = random.randint(0, MAP_WIDTH)
                    by = random.randint(0, MAP_HEIGHT)
                    if math.hypot(bx - player.rect.centerx, by - player.rect.centery) >= safe_dist:
                        break
                b = Boss(bx, by, player.level)
                boss_list.append(b)
                b.hit_flash_timer = 0.0
            player.new_level = False

        # Événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # au clic “Jouer” en menu principal, on affiche d’abord l’écran “touches” en fondu
        if main_menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if play_button_rect.collidepoint(event.pos):
                # 1) run the 7-image slideshow (skip on any key/mouse)
                show_story_slideshow(screen, clock)

                # 2) then show the controls screen (skip on any key/mouse)
                show_touches_screen(screen, clock)

                # 3) finally actually start the game
                main_menu   = False
                start_ticks = pygame.time.get_ticks()
                kills       = 0
                game_over   = False
                enemy_list.clear()
                mages.clear()
                xp_orbs.clear()
                boss_list.clear()
                player.__init__(MAP_WIDTH // 2, MAP_HEIGHT // 2)
                cam_x = max(0, min(player.rect.centerx - WIDTH//2, MAP_WIDTH  - WIDTH))
                cam_y = max(0, min(player.rect.centery  - HEIGHT//2, MAP_HEIGHT - HEIGHT))

            continue

        if not main_menu and not game_over and not upgrade_active:
            # on délègue au helper
            if handle_scream_input(event, player, enemy_list, mages, cam_x, cam_y):
                pass
                 # ou juste passer à la suite
        if upgrade_active and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for key, rect in zip(upgrade_menu.choices, upgrade_menu.rects):
                if rect.collidepoint(event.pos):
                    # applique tout de suite l'amélioration
                    player.apply_upgrade(key)
                    # on coupe le menu et on force le fade-out
                    upgrade_active = False
                    upgrade_fade   = fade_in_dur    # démarrer le fondu sortant
                    upgrade_resume_timer = 0.7
                    break

        if upgrade_resume_timer > 0:
            upgrade_resume_timer -= dt

        if main_menu:
            screen.blit(main_menu_img, (0,0))
            pygame.display.flip()
            continue

        # Caméra
        cam_x = max(0, min(player.rect.centerx - WIDTH//2, MAP_WIDTH  - WIDTH))
        cam_y = max(0, min(player.rect.centery  - HEIGHT//2, MAP_HEIGHT - HEIGHT))

        # Boucle de jeu
        if upgrade_resume_timer <= 0 and not upgrade_active and not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys, dt)

            # Auto-attack (inclut boss)
            if player.auto_attack and (enemy_list or mages or boss_list):
                targets = enemy_list + mages + boss_list
                t = min(targets, key=lambda e: math.hypot(e.rect.centerx-player.rect.centerx,
                                                          e.rect.centery-player.rect.centery))
                player.attack(targets, t.rect.center)
                if t in boss_list:
                    hit_flash_timer   = HIT_FLASH_DURATION
                    hit_flash_target  = b       # on conserve la référence à l’objet Boss

            # Clic pour attaquer
            elif pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                world_pos = (mx+cam_x, my+cam_y)
                player.attack(enemy_list + mages + boss_list, world_pos)
                for b in boss_list:
                    if b.rect.collidepoint(world_pos):
                        hit_flash_timer   = HIT_FLASH_DURATION
                        hit_flash_target  = b       # on conserve la référence à l’objet Boss

            # Spawn gobelins/mages
            game_time    = (pygame.time.get_ticks() - start_ticks) / 1000
            elite_chance = min(0.1, player.level * 0.005)
            rare_chance  = min(0.3, player.level * 0.015)
            time_mod     = 1 + game_time / 60
            level_mod    = max(0.2, 1 - player.level * 0.01)
            interval     = max(0.05, base_spawn_interval * level_mod / time_mod)
            spawn_timer += dt
            if spawn_timer >= interval:
                spawn_timer = 0.0
            # — Cap dynamique lié au niveau —
                current_enemies = len(enemy_list) + len(mages) + len(boss_list)
                cap = BASE_MAX_ENEMIES + PER_LEVEL_ENEMIES * (player.level - 1)
                if current_enemies >= cap:
                    continue   # on saute ce spawn-ci



                edge = random.choice(['top','bottom','left','right'])
                if edge == 'top':
                    x = random.randint(int(cam_x), int(cam_x + WIDTH));  y = cam_y - 50
                elif edge == 'bottom':
                    x = random.randint(int(cam_x), int(cam_x + WIDTH));  y = cam_y + HEIGHT + 50
                elif edge == 'left':
                    x = cam_x - 50; y = random.randint(int(cam_y), int(cam_y + HEIGHT))
                else:
                    x = cam_x + WIDTH + 50; y = random.randint(int(cam_y), int(cam_y + HEIGHT))
                if random.random() < mage_spawn_chance:
                    mages.append(GoblinMage(x, y))
                else:
                    r = random.random()
                    tier = 'elite' if r < elite_chance else 'rare' if r < elite_chance+rare_chance else 'normal'
                    enemy_list.append(Enemy(x, y, speed=60, tier=tier, player_level=player.level))

            # Update gobelins/mages
            for e in enemy_list: e.update(player.rect.center, dt)
            for m in mages:      m.update(player, dt, cam_x, cam_y)

            # Update & attaque bosses
            for b in boss_list:
                b.update(player.rect.center, dt)
                dx = b.rect.centerx - player.rect.centerx
                dy = b.rect.centery  - player.rect.centery
                if math.hypot(dx, dy) <= b.attack_range and b.attack_timer <= 0:
                    player.take_damage(b.damage)
                    b.attack_timer = b.attack_cooldown
                    screen_flash_timer = FLASH_DURATION

            for b in boss_list[:]:
                if b.hp <= 0:
                    xp_orbs.append(XPOrb(b.rect.centerx, b.rect.centery, b.xp_value))
                    boss_list.remove(b)
                    if hit_flash_target is b:
                        hit_flash_target = None


            # Separation
            all_entities = enemy_list+mages
            for i in range(len(all_entities)):
                e1=all_entities[i]
                for e2 in all_entities[i+1:]:
                    dx=e1.rect.centerx-e2.rect.centerx; dy=e1.rect.centery-e2.rect.centery
                    dist=math.hypot(dx,dy); md=(e1.rect.width+e2.rect.width)/2
                    if 0<dist<md:
                        nx,ny=dx/dist,dy/dist; overlap=md-dist
                        e1.rect.x+=nx*overlap*0.5; e1.rect.y+=ny*overlap*0.5
                        e2.rect.x-=nx*overlap*0.5; e2.rect.y-=ny*overlap*0.5

            # Collisions & kills
            inset=50
            for e in enemy_list[:]:
                hb=player.rect.inflate(-inset,-inset)
                if e.rect.colliderect(hb) and e.attack_timer<=0:
                    player.take_damage(e.damage); e.attack_timer=e.attack_cooldown; e.pause_timer=0.5; screen_flash_timer=FLASH_DURATION
                if e.hp<=0:
                    kills+=1; xp_orbs.append(XPOrb(e.rect.centerx,e.rect.centery,e.xp_value)); enemy_list.remove(e)
                elif math.hypot(e.rect.centerx-player.rect.centerx,e.rect.centery-player.rect.centery)>max(WIDTH,HEIGHT)*2:
                    enemy_list.remove(e)

            # XP orbs & magnet
            for orb in xp_orbs:
                if player.magnet_active:
                    orb.attract_radius=float('inf'); f=3+(player.magnet_duration-player.magnet_timer)/player.magnet_duration; orb.attract_speed=orb.base_attract_speed*f
                else:
                    orb.attract_radius=orb.base_attract_radius; orb.attract_speed=orb.base_attract_speed
                orb.update(dt,player.rect.center)
            for orb in xp_orbs[:]:
                if orb.rect.colliderect(player.rect):
                    orb.pickup_sound.play(); player.gain_xp(orb.value); xp_orbs.remove(orb)

            if current_bonus is None:
                btype=random.choice(BONUS_TYPES); bx,by=random.choice(bonus_spawn_points)
                current_bonus=(btype,pygame.Rect(bx,by,BONUS_SIZE,BONUS_SIZE))
            else:
                _,br=current_bonus
                if player.rect.colliderect(br):
                    player.apply_bonus(_); current_bonus=None

            for m in mages:
                for fb in m.projectiles[:]:
                    if fb.rect.colliderect(player.rect):
                        player.take_damage(2); m.projectiles.remove(fb); screen_flash_timer=FLASH_DURATION
            for m in mages[:]:
                if m.hp<=0:
                    kills+=1; xp_orbs.append(XPOrb(m.rect.centerx,m.rect.centery,m.xp_value)); mages.remove(m)

            game_time=(pygame.time.get_ticks()-start_ticks)/1000
            if player.hp<=0:
                game_over=True; survival_time=game_time

 # --- DESSIN ---
        draw_tiled_background(screen, cam_x, cam_y, bg_img, bg_w, bg_h)
        for orb in xp_orbs: orb.draw(screen, cam_x, cam_y)
        if current_bonus:
            _, br = current_bonus
            screen.blit(magnet_img, (br.x - cam_x, br.y - cam_y))
        for e in enemy_list:
            e.draw(screen, cam_x, cam_y)
            ex, ey = e.rect.x - cam_x, e.rect.y - cam_y
            bw, bh = e.rect.width, 5
            pygame.draw.rect(screen, (100,0,0), (ex, ey-bh-2, bw, bh))
            pygame.draw.rect(screen, (0,200,0), (ex, ey-bh-2, int(bw*(e.hp/e.max_hp)), bh))
        for m in mages:
            m.draw(screen, cam_x, cam_y)

        # Dessin des bosses
        for b in boss_list:
            b.draw(screen, cam_x, cam_y)
            # barre de vie
            hp_w, hp_h = b.rect.width, 5
            ex, ey = b.rect.x - cam_x, b.rect.y - cam_y - 10
            pygame.draw.rect(screen, (100,0,0), (ex, ey, hp_w, hp_h))
            pygame.draw.rect(screen, (200,0,0), (ex, ey, int(hp_w*(b.hp/b.max_hp)), hp_h))

        # Flash blanc localisé sur le boss touché
# Flash blanc localisé sur le boss touché, en respectant la forme du sprite
# FLASH BLANC LOCALISÉ SUR LE BOSS TOUCHÉ
        if hit_flash_timer > 0 and hit_flash_target:
            a = int(255 * (hit_flash_timer / HIT_FLASH_DURATION))
            # copie du sprite (avec son canal alpha)
            flash_img = hit_flash_target.image.copy()
            # multiplie les pixels opaques par du blanc semi-transparent
            flash_img.fill((255,255,255,a), special_flags=pygame.BLEND_RGBA_MULT)
            # blit à la position du boss
            screen.blit(flash_img,
                        (hit_flash_target.rect.x - cam_x,
                        hit_flash_target.rect.y - cam_y))

        player.draw(screen, cam_x, cam_y)
        draw_bottom_overlay(screen, bottom_overlay, y_offset=overlay_y_offset, zoom=overlay_zoom)

        globe_x,globe_y,radius = 150,HEIGHT-150,100
        draw_health_globe(screen,globe_x,globe_y,radius,max(player.hp,0)/player.max_hp)

        # Dash bar
        bw,bh=40,9; px=player.rect.centerx-cam_x; py=player.rect.bottom-cam_y+6
        pygame.draw.rect(screen,(50,50,50),(px-bw//2,py,bw,bh))
        ratio=1.0 if player.dash_timer<=0 else max(0,1-player.dash_timer/player.dash_cooldown)
        pygame.draw.rect(screen,(0,200,200),(px-bw//2,py,int(bw*ratio),bh))
        pygame.draw.rect(screen,(255,255,255),(px-bw//2,py,bw,bh),1)

        # XP bar & level
        xr=player.xp/player.next_level_xp; bar_w,bar_h=300,8; bx=(WIDTH-bar_w)//2; by=20
        pygame.draw.rect(screen,(50,50,50),(bx,by,bar_w,bar_h))
        pygame.draw.rect(screen,(200,200,0),(bx,by,int(bar_w*xr),bar_h))
        pygame.draw.rect(screen,(255,255,255),(bx,by,bar_w,bar_h),2)
        FONT_HUD = pygame.freetype.Font(
            resource_path("assets/fonts/Cinzel/static/Cinzel-Regular.ttf"),
            24
        )

        ts,tr=FONT_HUD.render(f"Level: {player.level}",fgcolor=(255,255,255))
        tr.midtop=(WIDTH//2,by+bar_h+5); screen.blit(ts,tr)
        draw_scream_cooldown(screen, player)

        if upgrade_active or upgrade_fade > 0:
            # on augmente fade si on vient d'ouvrir, sinon on diminue
            if upgrade_active:
                upgrade_fade = min(upgrade_fade + dt, fade_in_dur)
                show_cards  = True
            else:
                upgrade_fade = max(upgrade_fade - dt, 0)
                show_cards  = False
            alpha = int(255 * (upgrade_fade / fade_in_dur))
            # ne dessine les cartes qu'en phase de fade-in (upgrade_active=True)
            upgrade_menu.draw(screen, alpha, show_cards)
        if game_over:
            screen.fill((0,0,0))
            f1=pygame.font.Font(None,72); f2=pygame.font.Font(None,48)
            lines=["GAME OVER",f"Survived: {survival_time:.1f}s",f"Level:    {player.level}",f"Kills:    {kills}"]
            for i,t in enumerate(lines):
                fn=f1 if i==0 else f2; surf=fn.render(t,True,(255,255,255))
                screen.blit(surf,((WIDTH-surf.get_width())//2,150+i*80))

        if not game_over and screen_flash_timer > 0:
            a = int(255 * 0.5 * (screen_flash_timer / FLASH_DURATION))
            fs = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            fs.fill((255, 0, 0, a))
            screen.blit(fs, (0, 0))

        pygame.display.flip()

if __name__ == "__main__":
    main()
