# boss.py
import pygame, math
from .enemy import Enemy
from .settings import MAP_WIDTH, MAP_HEIGHT
from .utils import resource_path
class Boss(Enemy):
    def __init__(self, x, y, player_level):
        super().__init__(x, y, speed=40, tier='elite', player_level=player_level)
        
        # Sprite agrandi
        self.image = pygame.transform.rotozoom(self.image, 0, 2.0)
        self.rect  = self.image.get_rect(center=self.rect.center)
        
        # Beaucoup plus de PV
        self.max_hp = int(self.max_hp * 5)
        self.hp     = self.max_hp
        
        # Teinte rouge
        self.tint_color = (255, 0, 0, 120)
        
        # XP
        self.xp_value = player_level * 10

        # --- Nouveaux réglages ---
        # 1) Dégâts faibles (ici 1 dégât par 5 niveaux, min 1)
        self.damage = max(1, player_level // 5)
        # 2) Cooldown long pour laisser respirer le joueur
        self.attack_cooldown = 3.0
        self.attack_timer    = 0.0
        # 3) Portée de la mêlée (ici la moitié de la largeur du sprite)
        self.attack_range = max(self.rect.width, self.rect.height) * 0.5
