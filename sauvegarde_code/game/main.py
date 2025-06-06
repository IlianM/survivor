import pygame
import pygame.gfxdraw
import random
import math
import sys
import os
import pygame.surfarray as surfarray
import numpy as np

<<<<<<< HEAD
# Imports avec gestion des imports relatifs/absolus
try:
    # Essayer les imports relatifs d'abord (pour l'exécution normale)
    from .settings import *
    from .player import Player
    from .enemy import Enemy
    from .xp_orb import XPOrb
    from .goblin_mage import GoblinMage
    from .boss import Boss
    from .balance_menu import BalanceMenu
    from .pause_system import pause_system
    from .balance_manager import balance
    from .settings_menu import SettingsMenu
    from .settings_manager import settings
    from .audio_manager import audio_manager
    from .settings import WIDTH, HEIGHT
except ImportError:
    # Si les imports relatifs échouent, essayer les imports absolus (pour PyInstaller)
    try:
        from settings import *
        from player import Player
        from enemy import Enemy
        from xp_orb import XPOrb
        from goblin_mage import GoblinMage
        from boss import Boss
        from balance_menu import BalanceMenu
        from pause_system import pause_system
        from balance_manager import balance
        from settings_menu import SettingsMenu
        from settings_manager import settings
        from audio_manager import audio_manager
        from settings import WIDTH, HEIGHT
    except ImportError as e:
        print(f"Erreur d'import: {e}")
        print("Assurez-vous que tous les fichiers du jeu sont présents.")
        sys.exit(1)
=======
from .settings import *
from .player import Player
from .enemy import Enemy
from .xp_orb import XPOrb
from .goblin_mage import GoblinMage
from .boss import Boss
from PIL import Image
from .utils import resource_path
>>>>>>> d955c0448de1a91383f7b2e524616f150efecce2

from PIL import Image

# — Globals that must be loaded after pygame.display is ready —
ICON_SIZE       = 64
CRI_ICON_PATH   = os.path.join("assets", "cri.png")
CRI_ICON        = None
CRI_ICON_GRAY   = None
FONT_SMALL      = None

HEALTH_ORNAMENT = None
HEALTH_TEXTURE  = None

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
    """Dessine le background avec tiling en utilisant les dimensions dynamiques de l'écran."""
    screen_w, screen_h = surf.get_size()
    
    # Calculer le décalage pour créer l'effet de scrolling
    ox = -(cx % bg_w)
    oy = -(cy % bg_h)
    
    # Dessiner les tuiles en commençant légèrement en dehors de l'écran pour éviter les gaps
    y = oy - bg_h
    while y < screen_h + bg_h:  # Ajouter une tuile supplémentaire pour éviter les bugs de bord
        x = ox - bg_w
        while x < screen_w + bg_w:  # Ajouter une tuile supplémentaire pour éviter les bugs de bord
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

    def open(self, screen_width, screen_height):
        """Ouvre le menu d'upgrade avec les dimensions actuelles de l'écran."""
        self.choices = random.sample(Player.UPGRADE_KEYS, 3)
        self.rects.clear()
        n = len(self.choices)
        group_w    = n * self.btn_w + (n - 1) * self.margin
        start_x    = (screen_width - group_w) // 2
        y          = (screen_height - self.btn_h) // 2
        for i, key in enumerate(self.choices):
            x = start_x + i * (self.btn_w + self.margin)
            self.rects.append(pygame.Rect(x, y, self.btn_w, self.btn_h))

    def draw(self, surf, alpha=255, show_choices=True):
        """Dessine le menu d'upgrade avec les dimensions actuelles de l'écran."""
        screen_width, screen_height = surf.get_size()
        ov = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
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


# Fonctions draw_bottom_overlay et draw_health_globe supprimées
# Code optimisé intégré directement dans la boucle principale pour de meilleures performances


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

    # Afficher l'icône du cri
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

    # Charger les paramètres et appliquer la résolution
    screen_width, screen_height = settings.get_resolution()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Reincarnation of the unkillable last human against all gods")

    # Appliquer les paramètres audio
    settings.apply_audio_settings()

    # now that display is ready, you can safely call get_cri_icons() once
    get_cri_icons()

    # timers
    screen_flash_timer = 0.0
    FLASH_DURATION     = 0.08
    HIT_FLASH_DURATION = 0.05

    hit_flash_timer  = 0.0
    hit_flash_target = None

    global HEALTH_ORNAMENT, HEALTH_TEXTURE
<<<<<<< HEAD
    bottom_overlay_original = pygame.image.load("assets/bottom_overlay.png").convert_alpha()
    HEALTH_ORNAMENT  = pygame.image.load("assets/health_orb_ornement.png").convert_alpha()
    HEALTH_TEXTURE   = pygame.image.load("assets/health_texture.png").convert_alpha()
=======
    bottom_overlay   = pygame.image.load(resource_path("assets/bottom_overlay.png")).convert_alpha()
    HEALTH_ORNAMENT  = pygame.image.load(resource_path("assets/health_orb_ornement.png")).convert_alpha()
    HEALTH_TEXTURE   = pygame.image.load(resource_path("assets/health_texture.png")).convert_alpha()
>>>>>>> d955c0448de1a91383f7b2e524616f150efecce2

    # Variables HUD avec scaling optimisé
    hud_scale = settings.get_hud_scale()
    
    # Cache des images redimensionnées pour optimiser les FPS
    scaled_images_cache = {}
    
    def get_scaled_overlay(scale):
        """Retourne le bottom overlay avec la bonne échelle, en utilisant un cache."""
        if scale not in scaled_images_cache:
            new_size = (
                int(bottom_overlay_original.get_width() * scale * 0.9),
                int(bottom_overlay_original.get_height() * scale * 0.9)
            )
            scaled_images_cache[scale] = pygame.transform.smoothscale(bottom_overlay_original, new_size)
        return scaled_images_cache[scale]
    
    def get_scaled_ornament(scale, diameter):
        """Retourne l'ornement de santé avec la bonne échelle."""
        cache_key = f"ornament_{scale}_{diameter}"
        if cache_key not in scaled_images_cache:
            orn_size = diameter + 4 + int(40 * scale)
            scaled_images_cache[cache_key] = pygame.transform.smoothscale(HEALTH_ORNAMENT, (orn_size, orn_size))
        return scaled_images_cache[cache_key]

    clock = pygame.time.Clock()
<<<<<<< HEAD
    pygame.mixer.music.load(os.path.join("fx", "background_music.mp3"))
    pygame.mixer.music.set_volume(settings.get_master_volume() * settings.get("audio.music_volume", 0.5))
    pygame.mixer.music.play(-1, fade_ms=2000)

    main_menu       = True
    in_settings     = False  # Nouvel état pour le menu paramètres
    raw_menu        = pygame.image.load("assets/main_menu.png").convert()
    main_menu_img   = pygame.transform.scale(raw_menu, (screen_width, screen_height))
    
    # Boutons du menu principal
    play_button_rect     = pygame.Rect(screen_width//2 - 175, screen_height//2 + 50, 350, 60)
    settings_button_rect = pygame.Rect(screen_width//2 - 175, screen_height//2 + 130, 350, 60)
=======
    pygame.mixer.music.load(resource_path("fx/background_music.mp3"))

    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, fade_ms=2000)

    main_menu       = True
    raw_menu = pygame.image.load(resource_path("assets/main_menu.png")).convert()

    main_menu_img   = pygame.transform.scale(raw_menu, (WIDTH, HEIGHT))
    play_button_rect= pygame.Rect(WIDTH//2 - 210, HEIGHT//2 + 50, 350, 120)
>>>>>>> d955c0448de1a91383f7b2e524616f150efecce2

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
    start_ticks         = 0
    kills               = 0
    game_over           = False
    survival_time       = 0.0
    game_start_time     = 0  # Timer de jeu depuis le début

    upgrade_menu         = UpgradeMenu()
    upgrade_active       = False
    upgrade_fade         = 0.0
    fade_in_dur          = 0.5
    fade_out_dur         = 1.0
    upgrade_resume_timer = 0.0

    # MENU D'ÉQUILIBRAGE INTÉGRÉ
    balance_menu = BalanceMenu(screen_width, screen_height)
    print("🎮 Menu d'équilibrage intégré activé ! Appuyez sur F1 pendant le jeu.")
    
    # MENU DE PARAMÈTRES INTÉGRÉ
    settings_menu = SettingsMenu(screen_width, screen_height)
    print("⚙️ Menu de paramètres intégré ! Bouton paramètres dans le menu principal.")

    while True:
        dt = clock.tick(FPS) / 1000
        
        # Vérifier si la résolution a changé
        current_resolution = settings.get_resolution()
        if (screen_width, screen_height) != current_resolution:
            screen_width, screen_height = current_resolution
            screen = pygame.display.set_mode((screen_width, screen_height))
            main_menu_img = pygame.transform.scale(raw_menu, (screen_width, screen_height))
            # Recalculer les positions des boutons
            play_button_rect = pygame.Rect(screen_width//2 - 175, screen_height//2 + 50, 350, 60)
            settings_button_rect = pygame.Rect(screen_width//2 - 175, screen_height//2 + 130, 350, 60)
            # Recréer les menus avec nouvelle taille
            balance_menu = BalanceMenu(screen_width, screen_height)
            settings_menu = SettingsMenu(screen_width, screen_height)
        
        # Mettre à jour l'échelle HUD avec cache
        new_hud_scale = settings.get_hud_scale()
        if new_hud_scale != hud_scale:
            hud_scale = new_hud_scale
            # Vider le cache si l'échelle a changé
            scaled_images_cache.clear()
        
        # Mettre à jour les volumes audio si nécessaire
        audio_manager.update_all_volumes()
        
        # SYSTÈME DE PAUSE INTÉGRÉ
        adjusted_dt = pause_system.update(dt)
        
        screen_flash_timer = max(0.0, screen_flash_timer - adjusted_dt)
        hit_flash_timer    = max(0.0, hit_flash_timer    - adjusted_dt)

        hit_flash_timer = max(0.0, hit_flash_timer - adjusted_dt)
        if hit_flash_timer == 0:
            hit_flash_target = None

        # Level up → menu + boss spawn
        if player.new_level:
            upgrade_menu.open(screen_width, screen_height)
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

            # MENU DE PARAMÈTRES - Gestion prioritaire
            if settings_menu.handle_event(event):
                continue  # Événement absorbé par le menu paramètres

            # MENU D'ÉQUILIBRAGE - Gestion F1
            f1_handled = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1 and not main_menu:
                balance_menu.toggle()
                if balance_menu.active:
                    pause_system.pause()
                    print("⏸️ Jeu mis en pause pour équilibrage")
                else:
                    pause_system.resume()
                    print("▶️ Jeu repris")
                f1_handled = True  # Marquer que F1 a été traité

            # CORRECTION: Laisser le système de pause gérer ses événements seulement si le menu d'équilibrage est actif
            if not main_menu and balance_menu.active:
                pause_system.handle_event(event)

            # Laisser le menu d'équilibrage gérer ses événements (SAUF si F1 vient d'être traité)
            if not main_menu and not f1_handled and balance_menu.handle_event(event):
                continue  # Événement absorbé par le menu

            # GESTION MENU PRINCIPAL AVEC BOUTONS
            if main_menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button_rect.collidepoint(event.pos):
                    # 1) run the 7-image slideshow (skip on any key/mouse)
                    show_story_slideshow(screen, clock)

                    # 2) then show the controls screen (skip on any key/mouse)
                    show_touches_screen(screen, clock)

                    # 3) finally actually start the game
                    main_menu   = False
                    start_ticks = pygame.time.get_ticks()
                    game_start_time = pygame.time.get_ticks()
                    kills       = 0
                    game_over   = False
                    enemy_list.clear()
                    mages.clear()
                    xp_orbs.clear()
                    boss_list.clear()
                    player.__init__(MAP_WIDTH // 2, MAP_HEIGHT // 2)
                    cam_x = max(0, min(player.rect.centerx - screen_width//2, MAP_WIDTH - screen_width))
                    cam_y = max(0, min(player.rect.centery - screen_height//2, MAP_HEIGHT - screen_height))
                    continue
                
                elif settings_button_rect.collidepoint(event.pos):
                    # Ouvrir le menu paramètres
                    settings_menu.toggle()
                    print("⚙️ Paramètres ouverts depuis le menu principal")
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

        # Mise à jour des menus
        settings_menu.update(dt)
        
        if upgrade_resume_timer > 0:
            upgrade_resume_timer -= adjusted_dt

        if main_menu:
            # Dessiner le menu principal avec boutons
            screen.blit(main_menu_img, (0,0))
            
            # Créer une police pour les boutons
            try:
                button_font = pygame.font.Font(None, 36)
            except:
                button_font = pygame.font.SysFont('Arial', 36)
            
            # Dessiner bouton Jouer
            mouse_pos = pygame.mouse.get_pos()
            play_hover = play_button_rect.collidepoint(mouse_pos)
            play_color = (100, 150, 255) if play_hover else (70, 70, 80)
            pygame.draw.rect(screen, play_color, play_button_rect)
            pygame.draw.rect(screen, (255, 255, 255), play_button_rect, 3)
            
            play_text = button_font.render("JOUER", True, (255, 255, 255))
            play_text_rect = play_text.get_rect(center=play_button_rect.center)
            screen.blit(play_text, play_text_rect)
            
            # Dessiner bouton Paramètres
            settings_hover = settings_button_rect.collidepoint(mouse_pos)
            settings_color = (100, 150, 255) if settings_hover else (70, 70, 80)
            pygame.draw.rect(screen, settings_color, settings_button_rect)
            pygame.draw.rect(screen, (255, 255, 255), settings_button_rect, 3)
            
            settings_text = button_font.render("PARAMETRES", True, (255, 255, 255))
            settings_text_rect = settings_text.get_rect(center=settings_button_rect.center)
            screen.blit(settings_text, settings_text_rect)
            
            # Dessiner le menu paramètres s'il est ouvert
            settings_menu.draw(screen)
            
            pygame.display.flip()
            continue

        # Caméra avec limites strictes pour éviter les bugs visuels
        # Gérer le cas où la map est plus petite que l'écran
        if MAP_WIDTH <= screen_width:
            cam_x = (MAP_WIDTH - screen_width) // 2
        else:
            cam_x = max(0, min(player.rect.centerx - screen_width//2, MAP_WIDTH - screen_width))
            
        if MAP_HEIGHT <= screen_height:
            cam_y = (MAP_HEIGHT - screen_height) // 2
        else:
            cam_y = max(0, min(player.rect.centery - screen_height//2, MAP_HEIGHT - screen_height))
        
        # S'assurer que la caméra reste dans les limites valides
        cam_x = max(0, min(cam_x, MAP_WIDTH - screen_width)) if MAP_WIDTH > screen_width else 0
        cam_y = max(0, min(cam_y, MAP_HEIGHT - screen_height)) if MAP_HEIGHT > screen_height else 0

        # Boucle de jeu
        if upgrade_resume_timer <= 0 and not upgrade_active and not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys, adjusted_dt)

            # Auto-attack (inclut boss)
            if player.auto_attack and (enemy_list or mages or boss_list):
                targets = enemy_list + mages + boss_list
                t = min(targets, key=lambda e: math.hypot(e.rect.centerx-player.rect.centerx,
                                                          e.rect.centery-player.rect.centery))
                player.attack(targets, t.rect.center)
                if t in boss_list:
                    hit_flash_timer   = HIT_FLASH_DURATION
                    hit_flash_target  = b       # on conserve la référence à l'objet Boss

            # Clic pour attaquer
            elif pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                world_pos = (mx+cam_x, my+cam_y)
                player.attack(enemy_list + mages + boss_list, world_pos)
                for b in boss_list:
                    if b.rect.collidepoint(world_pos):
                        hit_flash_timer   = HIT_FLASH_DURATION
                        hit_flash_target  = b       # on conserve la référence à l'objet Boss

            # Spawn gobelins/mages
            game_time    = (pygame.time.get_ticks() - start_ticks) / 1000
            
            # NOUVEAU: Variables de scaling depuis balance.json
            scaling_config = balance.config.get("scaling", {})
            tier_chances = scaling_config.get("enemy_tier_chances", {})
            time_scaling = scaling_config.get("time_scaling", {})
            spawning_config = balance.config.get("spawning", {})
            
            elite_chance = min(
                tier_chances.get("elite_chance_max", 0.1), 
                player.level * tier_chances.get("elite_chance_per_level", 0.005)
            )
            rare_chance = min(
                tier_chances.get("rare_chance_max", 0.3), 
                player.level * tier_chances.get("rare_chance_per_level", 0.015)
            )
            
            time_mod = 1 + game_time / time_scaling.get("time_modifier_divisor", 60)
            level_mod = max(
                time_scaling.get("level_modifier_min", 0.2), 
                1 - player.level * time_scaling.get("level_modifier_per_level", 0.01)
            )
            
            base_spawn_interval = spawning_config.get("base_spawn_rate", 3.0)
            interval = max(
                time_scaling.get("minimum_spawn_interval", 0.05), 
                base_spawn_interval * level_mod / time_mod
            )
            
            spawn_timer += adjusted_dt
            if spawn_timer >= interval:
                spawn_timer = 0.0
            # — Cap dynamique lié au niveau —
                current_enemies = len(enemy_list) + len(mages) + len(boss_list)
                cap = spawning_config.get("base_max_enemies", 5) + spawning_config.get("per_level_enemies", 2) * (player.level - 1)
                if current_enemies >= cap:
                    continue   # on saute ce spawn-ci

                edge = random.choice(['top','bottom','left','right'])
                if edge == 'top':
                    x = random.randint(int(cam_x), int(cam_x + screen_width));  y = cam_y - 50
                elif edge == 'bottom':
                    x = random.randint(int(cam_x), int(cam_x + screen_width));  y = cam_y + screen_height + 50
                elif edge == 'left':
                    x = cam_x - 50; y = random.randint(int(cam_y), int(cam_y + screen_height))
                else:
                    x = cam_x + screen_width + 50; y = random.randint(int(cam_y), int(cam_y + screen_height))
                    
                mage_spawn_chance = spawning_config.get("mage_spawn_chance", 0.1)
                if random.random() < mage_spawn_chance:
                    mages.append(GoblinMage(x, y))
                else:
                    r = random.random()
                    tier = 'elite' if r < elite_chance else 'rare' if r < elite_chance+rare_chance else 'normal'
                    enemy_list.append(Enemy(x, y, speed=60, tier=tier, player_level=player.level))

            # Update gobelins/mages
            for e in enemy_list: e.update(player.rect.center, adjusted_dt)
            for m in mages:      m.update(player, adjusted_dt, cam_x, cam_y)

            # Update & attaque bosses
            for b in boss_list:
                b.update(player.rect.center, adjusted_dt)
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
                elif math.hypot(e.rect.centerx-player.rect.centerx,e.rect.centery-player.rect.centery)>max(screen_width,screen_height)*2:
                    enemy_list.remove(e)

            # XP orbs & magnet
            for orb in xp_orbs:
                if player.magnet_active:
                    orb.attract_radius=float('inf'); f=3+(player.magnet_duration-player.magnet_timer)/player.magnet_duration; orb.attract_speed=orb.base_attract_speed*f
                else:
                    orb.attract_radius=orb.base_attract_radius; orb.attract_speed=orb.base_attract_speed
                orb.update(adjusted_dt,player.rect.center)
            for orb in xp_orbs[:]:
                if orb.rect.colliderect(player.rect):
                    orb.play_pickup_sound(); player.gain_xp(orb.value); xp_orbs.remove(orb)

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
        
        # Bottom overlay optimisé avec cache
        bottom_overlay = get_scaled_overlay(hud_scale)
        overlay_rect = bottom_overlay.get_rect()
        # Descendre le bottom_overlay de 400 pixels vers le bas
        overlay_rect.midbottom = (screen_width // 2, screen_height + 330)
        screen.blit(bottom_overlay, overlay_rect)

        # HUD avec scaling optimisé
        scaled_globe_radius = int(100 * hud_scale)
        globe_x = int(150 * hud_scale)
        globe_y = screen_height - int(150 * hud_scale)
        
        # Health globe optimisé
        diameter = scaled_globe_radius * 2
        pygame.gfxdraw.filled_circle(screen, globe_x, globe_y, scaled_globe_radius, (0,0,0,128))
        
        hp_ratio = max(player.hp,0)/player.max_hp
        if hp_ratio > 0:
            level_y = globe_y + scaled_globe_radius - hp_ratio * diameter
            y_start = max(int(math.ceil(level_y)), globe_y - scaled_globe_radius)
            y_end   = globe_y + scaled_globe_radius
            texture = pygame.transform.smoothscale(HEALTH_TEXTURE, (diameter, diameter))
            mask    = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            for y in range(y_start, y_end + 1):
                dy      = y - globe_y
                dx      = int(math.sqrt(scaled_globe_radius*scaled_globe_radius - dy*dy))
                local_y = y - (globe_y - scaled_globe_radius)
                local_x = (globe_x - dx) - (globe_x - scaled_globe_radius)
                mask.fill((255,255,255,255), (local_x, local_y, dx*2, 1))
            masked = texture.copy()
            masked.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(masked, (globe_x - scaled_globe_radius, globe_y - scaled_globe_radius))
        
        pygame.draw.circle(screen, (255,255,255), (globe_x, globe_y), scaled_globe_radius, 2)
        
        # Ornement optimisé avec cache
        ornament = get_scaled_ornament(hud_scale, diameter)
        ornament = pygame.transform.flip(ornament, True, False)
        orn_rect = ornament.get_rect(center=(globe_x, globe_y))
        screen.blit(ornament, orn_rect)

        # Dash bar avec scaling
        bw, bh = int(40 * hud_scale), int(9 * hud_scale)
        px = player.rect.centerx - cam_x
        py = player.rect.bottom - cam_y + 6
        pygame.draw.rect(screen, (50,50,50), (px-bw//2, py, bw, bh))
        ratio = 1.0 if player.dash_timer <= 0 else max(0, 1 - player.dash_timer/player.dash_cooldown)
        pygame.draw.rect(screen, (0,200,200), (px-bw//2, py, int(bw*ratio), bh))
        pygame.draw.rect(screen, (255,255,255), (px-bw//2, py, bw, bh), 1)

<<<<<<< HEAD
        # XP bar & level avec scaling
        xr = player.xp / player.next_level_xp
        bar_w, bar_h = int(300 * hud_scale), int(8 * hud_scale)
        bx = (screen_width - bar_w) // 2
        by = int(20 * hud_scale)
        pygame.draw.rect(screen, (50,50,50), (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, (200,200,0), (bx, by, int(bar_w*xr), bar_h))
        pygame.draw.rect(screen, (255,255,255), (bx, by, bar_w, bar_h), 2)
        
        # Police HUD avec scaling
        try:
            font_size = int(24 * hud_scale)
            FONT_HUD = pygame.freetype.Font("assets/fonts/Cinzel-Regular.ttf", font_size)
        except:
            FONT_HUD = pygame.font.Font(None, font_size)
        
        ts, tr = FONT_HUD.render(f"Level: {player.level}", fgcolor=(255,255,255))
        tr.midtop = (screen_width//2, by + bar_h + 5)
        screen.blit(ts, tr)
        
        # Timer de jeu (si activé dans les paramètres)
        if settings.get_timer_enabled() and not main_menu and not game_over:
            elapsed_time = (pygame.time.get_ticks() - game_start_time) / 1000
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            timer_text = f"Temps: {minutes:02d}:{seconds:02d}"
            
            try:
                timer_font_size = int(20 * hud_scale)
                timer_font = pygame.font.Font(None, timer_font_size)
            except:
                timer_font = pygame.font.SysFont('Arial', timer_font_size)
            
            timer_surface = timer_font.render(timer_text, True, (255, 255, 255))
            timer_x = screen_width - timer_surface.get_width() - int(20 * hud_scale)
            timer_y = int(20 * hud_scale)
            
            # Fond semi-transparent pour le timer
            timer_bg = pygame.Rect(timer_x - 5, timer_y - 2, 
                                 timer_surface.get_width() + 10, 
                                 timer_surface.get_height() + 4)
            pygame.draw.rect(screen, (0, 0, 0, 150), timer_bg)
            screen.blit(timer_surface, (timer_x, timer_y))
        
=======
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
>>>>>>> d955c0448de1a91383f7b2e524616f150efecce2
        draw_scream_cooldown(screen, player)

        if upgrade_active or upgrade_fade > 0:
            # on augmente fade si on vient d'ouvrir, sinon on diminue
            if upgrade_active:
                upgrade_fade = min(upgrade_fade + adjusted_dt, fade_in_dur)
                show_cards  = True
            else:
                upgrade_fade = max(upgrade_fade - adjusted_dt, 0)
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
                screen.blit(surf,((screen_width-surf.get_width())//2,150+i*80))

        if not game_over and screen_flash_timer > 0:
            a = int(255 * 0.5 * (screen_flash_timer / FLASH_DURATION))
            fs = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            fs.fill((255, 0, 0, a))
            screen.blit(fs, (0, 0))

        # MENU D'ÉQUILIBRAGE INTÉGRÉ - Mise à jour et affichage
        balance_menu.update(adjusted_dt)
        
        # Rafraîchir les stats du joueur si le menu d'équilibrage est actif
        if balance_menu.active:
            player.refresh_balance_stats()
        
        # Overlay de pause (si en pause)
        if not main_menu:
            pause_system.draw_pause_overlay(screen)
        
        # Menu d'équilibrage (dessiné en dernier pour être au-dessus de tout)
        if not main_menu:
            balance_menu.draw(screen)
            
        # Menu de paramètres (au-dessus de tout)
        settings_menu.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()
