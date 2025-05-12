import pygame
import pygame.gfxdraw
import random
import math
import sys
import os

from .settings import *
from .player import Player
from .enemy import Enemy
from .xp_orb import XPOrb
from .goblin_mage import GoblinMage
from .boss import Boss

HEALTH_ORNAMENT = None
HEALTH_TEXTURE  = None

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
        self.choices = []
        self.rects   = []
        self.card_img = pygame.image.load("assets/upgrade_card.png").convert_alpha()
        self.btn_w, self.btn_h = self.card_img.get_size()
        self.margin = 20
        self.font_title = pygame.freetype.Font("assets/fonts/Cinzel-Regular.ttf", 24)
        self.font_body  = pygame.freetype.Font("assets/fonts/Cinzel-Regular.ttf", 16)

    def open(self):
        self.choices = random.sample(Player.UPGRADE_KEYS, 3)
        self.rects.clear()
        n = len(self.choices)
        group_width = n * self.btn_w + (n - 1) * self.margin
        start_x     = (WIDTH - group_width) // 2
        y           = (HEIGHT - self.btn_h) // 2
        for i in range(n):
            x = start_x + i * (self.btn_w + self.margin)
            self.rects.append(pygame.Rect(x, y, self.btn_w, self.btn_h))

    def draw(self, surf, alpha=255):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, alpha//2))
        surf.blit(ov, (0, 0))
        for key, rect in zip(self.choices, self.rects):
            surf.blit(self.card_img, rect.topleft)
            title_surf, title_rect = self.font_title.render(key, fgcolor=(255,255,255))
            title_rect.center = (rect.centerx, rect.centery - 30)
            surf.blit(title_surf, title_rect)
            info = Player.UPGRADE_INFO[key]
            if info["type"] == "flat":
                desc = f"+{info['value']} {info['unit']}"
            elif info["type"] == "percent":
                desc = f"+{int(info['value']*100)}% {info['unit']}"
            else:
                pct  = int((info["value"] - 1) * 100)
                sign = "+" if pct > 0 else ""
                desc = f"{sign}{pct}% {info['unit']}"
            desc_surf, desc_rect = self.font_body.render(desc, fgcolor=(200,200,200))
            desc_rect.center = (rect.centerx, rect.centery + 30)
            surf.blit(desc_surf, desc_rect)

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
        mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        for y in range(y_start, y_end + 1):
            dy = y - cy
            dx = int(math.sqrt(radius*radius - dy*dy))
            local_y  = y - (cy - radius)
            local_x1 = (cx - dx) - (cx - radius)
            mask.fill((255,255,255,255), (local_x1, local_y, dx*2, 1))
        masked = texture.copy()
        masked.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(masked, (cx - radius, cy - radius))
    pygame.draw.circle(surface, outline_color, (cx, cy), radius, outline_width)
    orn_size  = diameter + outline_width * 2 + 40
    ornament  = pygame.transform.smoothscale(HEALTH_ORNAMENT, (orn_size, orn_size))
    ornament  = pygame.transform.flip(ornament, True, False)
    orn_rect  = ornament.get_rect(center=(cx, cy))
    surface.blit(ornament, orn_rect)

def main():
    pygame.init()
    pygame.mixer.init()
    pygame.freetype.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Reincarnation of the unkillable last human against all gods")

    # timers
    screen_flash_timer = 0.0
    FLASH_DURATION     = 0.08
    HIT_FLASH_DURATION = 0.05

    # pour afficher le flash sur boss uniquement
# pour afficher le flash sur boss uniquement
    hit_flash_timer  = 0.0
    hit_flash_target = None     # ce sera l’instance Boss touchée

    global HEALTH_ORNAMENT, HEALTH_TEXTURE
    bottom_overlay  = pygame.image.load("assets/bottom_overlay.png").convert_alpha()
    HEALTH_ORNAMENT = pygame.image.load("assets/health_orb_ornement.png").convert_alpha()
    HEALTH_TEXTURE  = pygame.image.load("assets/health_texture.png").convert_alpha()

    overlay_y_offset = 335
    overlay_zoom     = 0.9

    clock = pygame.time.Clock()
    pygame.mixer.music.load(os.path.join("fx", "background_music.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, fade_ms=2000)

    main_menu     = True
    raw_menu      = pygame.image.load("assets/main_menu.png").convert()
    main_menu_img = pygame.transform.scale(raw_menu, (WIDTH, HEIGHT))
    play_button_rect = pygame.Rect(WIDTH//2 - 210, HEIGHT//2 + 50, 350, 120)

    BONUS_SIZE  = 64
    bg_img      = pygame.image.load("assets/background.png").convert()
    bg_w, bg_h  = bg_img.get_size()
    magnet_raw  = pygame.image.load("assets/magnet.png").convert_alpha()
    magnet_img  = pygame.transform.smoothscale(magnet_raw, (BONUS_SIZE, BONUS_SIZE))

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
    current_bonus = None

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

            if main_menu and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_button_rect.collidepoint(event.pos):
                    main_menu   = False
                    start_ticks = pygame.time.get_ticks()
                    kills       = 0
                    game_over   = False
                    enemy_list.clear()
                    mages.clear()
                    xp_orbs.clear()
                    boss_list.clear()
                    player.__init__(MAP_WIDTH // 2, MAP_HEIGHT // 2)
                continue

            if not main_menu and not game_over and not upgrade_active:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                    mx, my = pygame.mouse.get_pos()
                    player.scream(enemy_list, mages, (mx+cam_x, my+cam_y))

            if upgrade_active and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, rect in zip(upgrade_menu.choices, upgrade_menu.rects):
                    if rect.collidepoint(event.pos):
                        player.apply_upgrade(key)
                        upgrade_active       = False
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
        FONT_HUD=pygame.freetype.Font("assets/fonts/Cinzel-Regular.ttf",24)
        ts,tr=FONT_HUD.render(f"Level: {player.level}",fgcolor=(255,255,255))
        tr.midtop=(WIDTH//2,by+bar_h+5); screen.blit(ts,tr)

        if upgrade_active or (not player.new_level and upgrade_fade>0):
            if upgrade_active:
                upgrade_fade=min(upgrade_fade+dt,fade_in_dur)
            else:
                upgrade_fade=max(upgrade_fade-dt,0)
            alpha=int(255*(upgrade_fade/fade_in_dur))
            upgrade_menu.draw(screen,alpha)

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
