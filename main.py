import pygame
import random
import math
import sys
import os

from settings import *
from player import Player
from enemy import Enemy
from xp_orb import XPOrb
from goblin_mage import GoblinMage


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
        ov.fill((0, 0, 0, alpha // 2))
        surf.blit(ov, (0, 0))

        for key, rect in zip(self.choices, self.rects):
            info = Player.UPGRADE_INFO[key]
            if info["type"] == "flat":
                desc = f"+{info['value']} {info['unit']}"
            elif info["type"] == "percent":
                pct = int(info["value"] * 100)
                desc = f"+{pct}% {info['unit']}"
            else:
                pct = int((info["value"] - 1) * 100)
                sign = "+" if pct > 0 else ""
                desc = f"{sign}{pct}% {info['unit']}"

            pygame.draw.rect(surf, (50, 50, 50), rect)
            pygame.draw.rect(surf, (200, 200, 200), rect, 2)

            title = self.font.render(key, True, (255, 255, 255))
            surf.blit(title, (rect.x + 10, rect.y + 10))
            text = self.font.render(desc, True, (200, 200, 200))
            surf.blit(text, (rect.x + 10, rect.y + 40))


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


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Reincarnation of the unkillable last human against all gods")
    clock = pygame.time.Clock()

    # Musique de fond
    pygame.mixer.music.load(os.path.join("fx", "background_music.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, fade_ms=2000)

    # Menu principal
    main_menu     = True
    raw_menu      = pygame.image.load("assets/main_menu.png").convert()
    main_menu_img = pygame.transform.scale(raw_menu, (WIDTH, HEIGHT))
    play_button_rect = pygame.Rect(
        WIDTH//2 - 210,
        HEIGHT//2 + 50,
        350,
        120
    )

    # Décor tuilé
    bg_img = pygame.image.load("assets/background.png").convert()
    bg_w, bg_h = bg_img.get_size()

    # Entités
    player     = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2)
    enemy_list = []
    mages      = []
    xp_orbs    = []

    # — Bonus Aimant —
    BONUS_TYPES = ["magnet"]
    BONUS_SIZE  = 64
# juste après BONUS_SIZE
    OFFSET = 200

    bonus_spawn_points = [
        (OFFSET, OFFSET),
        (MAP_WIDTH  - BONUS_SIZE - OFFSET, OFFSET),
        (OFFSET, MAP_HEIGHT - BONUS_SIZE - OFFSET),
        (MAP_WIDTH  - BONUS_SIZE - OFFSET, MAP_HEIGHT - BONUS_SIZE - OFFSET),
    ]

    current_bonus = None

    # Timers & compteurs
    spawn_timer         = 0.0
    base_spawn_interval = 3.0
    mage_spawn_chance   = 0.1
    start_ticks         = 0
    kills               = 0
    game_over           = False
    survival_time       = 0.0

    # Menu d’amélioration
    upgrade_menu         = UpgradeMenu()
    upgrade_active       = False
    upgrade_fade         = 0.0
    fade_in_dur          = 0.5
    fade_out_dur         = 1.0
    upgrade_resume_timer = 0.0  # pause de 2s après choix

    running = True
    while running:
        dt = clock.tick(FPS) / 1000

        # --- ÉVÉNEMENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Clic “Jouer”
            if main_menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button_rect.collidepoint(event.pos):
                    main_menu   = False
                    start_ticks = pygame.time.get_ticks()
                    kills       = 0
                    game_over   = False
                    enemy_list.clear()
                    mages.clear()
                    xp_orbs.clear()
                    player.__init__(MAP_WIDTH // 2, MAP_HEIGHT // 2)
                continue

            # En jeu
            if not main_menu and not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        player.auto_attack = not player.auto_attack
                    elif event.key == pygame.K_k and not player.new_level:
                        upgrade_active = not upgrade_active
                        upgrade_fade   = 0.0 if upgrade_active else fade_out_dur

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if event.button == 1:
                        player.attack(enemy_list + mages, (mx + cam_x, my + cam_y))
                    elif event.button == 3:
                        world_pos = (mx + cam_x, my + cam_y)
                        player.scream(enemy_list, mages, world_pos)

            # Clic dans le menu d’amélioration
            if upgrade_active and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for key, rect in zip(upgrade_menu.choices, upgrade_menu.rects):
                    if rect.collidepoint(mx, my):
                        player.apply_upgrade(key)
                        player.new_level = False
                        upgrade_active       = False
                        upgrade_resume_timer = 0.7
                        break

        # Pause post-upgrade
        if upgrade_resume_timer > 0:
            upgrade_resume_timer -= dt

        # Affichage menu principal
        if main_menu:
            screen.blit(main_menu_img, (0, 0))
            overlay = pygame.Surface((play_button_rect.width, play_button_rect.height), pygame.SRCALPHA)
            screen.blit(overlay, (play_button_rect.x, play_button_rect.y))
            pygame.display.flip()
            continue

        # Ouvre le menu au level-up
        if player.new_level and not upgrade_active:
            upgrade_menu.open()
            upgrade_active = True
            upgrade_fade   = 0.0

        # Caméra
        cam_x = max(0, min(player.rect.centerx - WIDTH//2,  MAP_WIDTH - WIDTH))
        cam_y = max(0, min(player.rect.centery - HEIGHT//2, MAP_HEIGHT - HEIGHT))

        # Jeu en cours
        if upgrade_resume_timer <= 0 and not upgrade_active and not game_over:
            keys = pygame.key.get_pressed()
            player.update(keys, dt)

            # Auto-attaque
            if player.auto_attack and (enemy_list or mages):
                all_targets = enemy_list + mages
                target = min(
                    all_targets,
                    key=lambda e: math.hypot(
                        e.rect.centerx - player.rect.centerx,
                        e.rect.centery  - player.rect.centery
                    )
                )
                player.attack(all_targets, target.rect.center)
            elif pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                player.attack(enemy_list + mages, (mx + cam_x, my + cam_y))

            # Spawn dynamique
            game_time    = (pygame.time.get_ticks() - start_ticks) / 1000
            elite_chance = min(0.1, player.level * 0.005)
            rare_chance  = min(0.3, player.level * 0.015)
            time_mod     = 1 + game_time / 60
            level_mod    = max(0.2, 1 - player.level * 0.01)
            interval     = max(0.05, base_spawn_interval * level_mod / time_mod)

            spawn_timer += dt
            if spawn_timer >= interval:
                spawn_timer = 0.0
                margin = 50
                edge   = random.choice(['top','bottom','left','right'])
                if edge == 'top':
                    x = random.randint(int(cam_x), int(cam_x + WIDTH))
                    y = cam_y - margin
                elif edge == 'bottom':
                    x = random.randint(int(cam_x), int(cam_x + WIDTH))
                    y = cam_y + HEIGHT + margin
                elif edge == 'left':
                    x = cam_x - margin
                    y = random.randint(int(cam_y), int(cam_y + HEIGHT))
                else:
                    x = cam_x + WIDTH + margin
                    y = random.randint(int(cam_y), int(cam_y + HEIGHT))

                if random.random() < mage_spawn_chance:
                    mages.append(GoblinMage(x, y))
                else:
                    r = random.random()
                    if r < elite_chance:
                        tier = 'elite'
                    elif r < elite_chance + rare_chance:
                        tier = 'rare'
                    else:
                        tier = 'normal'
                    enemy_list.append(
                        Enemy(x, y, speed=60, tier=tier, player_level=player.level)
                    )

            # 1) Update gobelins
            for e in enemy_list:
                e.update(player.rect.center, dt)

            # 2) Update mages
            for m in mages:
                m.update(player, dt, cam_x, cam_y)

            # 3) Séparation
            all_enemies = enemy_list + mages
            for i in range(len(all_enemies)):
                e1 = all_enemies[i]
                for j in range(i+1, len(all_enemies)):
                    e2 = all_enemies[j]
                    dx = e1.rect.centerx - e2.rect.centerx
                    dy = e1.rect.centery   - e2.rect.centery
                    dist    = math.hypot(dx, dy)
                    min_dist = (e1.rect.width + e2.rect.width) * 0.5
                    if 0 < dist < min_dist:
                        nx, ny = dx/dist, dy/dist
                        overlap = min_dist - dist
                        shift_x = nx * overlap * 0.5
                        shift_y = ny * overlap * 0.5
                        e1.rect.x += shift_x; e1.rect.y += shift_y
                        e2.rect.x -= shift_x; e2.rect.y -= shift_y

            # 4) Collisions & morts gobelins
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
                dy = e.rect.centery  - player.rect.centery
                if math.hypot(dx, dy) > max(WIDTH, HEIGHT)*2:
                    enemy_list.remove(e)

            # 5) Orbes d’XP + magnet
    # 5) Orbes d’XP + magnet
            for orb in xp_orbs:
                if player.magnet_active:
                    # couvre toute la map
                    orb.attract_radius = float('inf')
                    # vitesse qui monte progressivement
                    elapsed = player.magnet_duration - player.magnet_timer
                    factor  = 3 + elapsed / player.magnet_duration
                    orb.attract_speed = orb.base_attract_speed * factor
                else:
                    # restore valeurs de base
                    orb.attract_radius = orb.base_attract_radius
                    orb.attract_speed  = orb.base_attract_speed

                orb.update(dt, player.rect.center)
            # Ramassage des orbes
            for orb in xp_orbs[:]:
                if orb.rect.colliderect(player.rect):
                    orb.pickup_sound.play()
                    player.gain_xp(orb.value)
                    xp_orbs.remove(orb)

            # 6) Spawn & pickup du bonus Aimant
            if current_bonus is None:
                btype = random.choice(BONUS_TYPES)
                bx, by = random.choice(bonus_spawn_points)
                bonus_rect = pygame.Rect(bx, by, BONUS_SIZE, BONUS_SIZE)
                current_bonus = (btype, bonus_rect)
            else:
                btype, bonus_rect = current_bonus
                if player.rect.colliderect(bonus_rect):
                    player.apply_bonus(btype)
                    current_bonus = None

            # 7) Collisions projectiles mage → joueur
            for m in mages:
                for fb in m.projectiles[:]:
                    if fb.rect.colliderect(player.rect):
                        player.take_damage(2)
                        m.projectiles.remove(fb)


            # 8) Mort & nettoyage des mages
            for m in mages[:]:
                if m.hp <= 0:
                    kills += 1
                    xp_orbs.append(XPOrb(
                        m.rect.centerx,
                        m.rect.centery,
                        m.xp_value
                    ))
                    mages.remove(m)

            # Game Over
            if player.hp <= 0:
                game_over     = True
                survival_time = game_time

        # --- DESSIN ---
        draw_tiled_background(screen, cam_x, cam_y, bg_img, bg_w, bg_h)

        # Orbes
        for orb in xp_orbs:
            orb.draw(screen, cam_x, cam_y)

        # Bonus Aimant
        if current_bonus:
            _, bonus_rect = current_bonus
            s = pygame.Surface((BONUS_SIZE, BONUS_SIZE), pygame.SRCALPHA)
            s.fill((255, 0, 0, 153))
            screen.blit(s, (bonus_rect.x - cam_x, bonus_rect.y - cam_y))

        # Gobelins
        for e in enemy_list:
            e.draw(screen, cam_x, cam_y)
            ex, ey = e.rect.x - cam_x, e.rect.y - cam_y
            bw, bh = e.rect.width, 5
            pygame.draw.rect(screen, (100, 0, 0), (ex, ey-bh-2, bw, bh))
            pygame.draw.rect(screen, (0,200,0), (ex, ey-bh-2, bw*(e.hp/e.max_hp), bh))

        # Mages
        for m in mages:
            m.draw(screen, cam_x, cam_y)

        # Joueur
        player.draw(screen, cam_x, cam_y)

                # — Indicateur de cooldown du dash —
        bar_w, bar_h = 40, 5
        px = player.rect.centerx - cam_x
        py = player.rect.bottom   - cam_y + 6
        # fond gris
        pygame.draw.rect(screen, (50,50,50), (px - bar_w//2, py, bar_w, bar_h))
        # remplissage proportionnel
        ratio = 1.0 if player.dash_timer <= 0 else max(0, 1 - player.dash_timer / player.dash_cooldown)
        pygame.draw.rect(screen, (0,200,200), (px - bar_w//2, py, int(bar_w * ratio), bar_h))
        # bordure blanche
        pygame.draw.rect(screen, (255,255,255), (px - bar_w//2, py, bar_w, bar_h), 1)


        # HUD - bottom center
        abw, abh = 300, 20
        ax = (WIDTH - abw) // 2
        ay = HEIGHT - 120
        pygame.draw.rect(screen, (50, 50, 50), (ax, ay, abw, abh))
        pr = max(player.armor, 0) / player.max_arm
        pygame.draw.rect(screen, (0, 150, 150), (ax, ay, abw * pr, abh))
        pygame.draw.rect(screen, (255, 255, 255), (ax, ay, abw, abh), 2)
        hy = ay + abh + 5
        pygame.draw.rect(screen, (100, 0, 0), (ax, hy, abw, abh))
        hr = max(player.hp, 0) / player.max_hp
        pygame.draw.rect(screen, (0, 200, 0), (ax, hy, abw * hr, abh))
        pygame.draw.rect(screen, (255, 255, 255), (ax, hy, abw, abh), 2)
        xy = hy + abh + 5
        pygame.draw.rect(screen, (80, 80, 0), (ax, xy, abw, 10))
        xr = player.xp / player.next_level_xp
        pygame.draw.rect(screen, (200, 200, 0), (ax, xy, abw * xr, 10))
        pygame.draw.rect(screen, (255, 255, 255), (ax, xy, abw, 10), 1)
        font = pygame.font.Font(None, 24)
        screen.blit(font.render(f"Level: {player.level}", True, (255, 255, 255)), (ax, xy + 15))

        # Menu d’amélioration en fondu
        if upgrade_active or (not player.new_level and upgrade_fade > 0):
            if upgrade_active:
                upgrade_fade = min(upgrade_fade + dt, fade_in_dur)
            else:
                upgrade_fade = max(upgrade_fade - dt, 0)
            alpha = int(255 * (upgrade_fade / fade_in_dur))
            upgrade_menu.draw(screen, alpha)

        # Écran Game Over
        if game_over:
            screen.fill((0, 0, 0))
            f1 = pygame.font.Font(None, 72)
            f2 = pygame.font.Font(None, 48)
            lines = [
                "GAME OVER",
                f"Survived: {survival_time:.1f}s",
                f"Level:    {player.level}",
                f"Kills:    {kills}"
            ]
            for i, text in enumerate(lines):
                fn   = f1 if i == 0 else f2
                surf = fn.render(text, True, (255, 255, 255))
                screen.blit(surf, ((WIDTH - surf.get_width()) // 2, 150 + i * 80))

        pygame.display.flip()

    # Fondu de sortie de la musique et fermeture
    pygame.mixer.music.fadeout(2000)
    pygame.time.delay(2000)
    pygame.quit()


if __name__ == "__main__":
    main()
