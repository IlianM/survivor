"""
Système de pause pour Death Must Pygame.
Permet de mettre en pause le jeu pour l'équilibrage.
"""

import pygame
from typing import Optional

class PauseSystem:
    """Gestionnaire de pause pour le jeu."""
    
    def __init__(self):
        self.paused = False
        self.pause_overlay: Optional[pygame.Surface] = None
        self.font = None
        self.balance_menu_active = False  # Nouveau: track si le menu d'équilibrage est ouvert
        self._init_font()
    
    def _init_font(self):
        """Initialise la police."""
        try:
            # S'assurer que pygame.font est initialisé
            if not pygame.get_init():
                pygame.init()
            if not pygame.font.get_init():
                pygame.font.init()
            self.font = pygame.font.Font(None, 48)
        except:
            try:
                pygame.font.init()
                self.font = pygame.font.SysFont('Arial', 48)
            except:
                self.font = None
    
    def set_balance_menu_active(self, active: bool):
        """Indique si le menu d'équilibrage est actif."""
        self.balance_menu_active = active
    
    def toggle_pause(self):
        """Active/désactive la pause."""
        self.paused = not self.paused
        print(f"🎮 Jeu {'en pause' if self.paused else 'reprend'}")
    
    def pause(self):
        """Met le jeu en pause."""
        if not self.paused:
            self.paused = True
            print("⏸️ Jeu mis en pause")
    
    def resume(self):
        """Reprend le jeu."""
        if self.paused:
            self.paused = False
            print("▶️ Jeu repris")
    
    def is_paused(self) -> bool:
        """Retourne True si le jeu est en pause."""
        return self.paused
    
    def handle_event(self, event) -> bool:
        """Gère les événements de pause."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # CORRECTION: N'activer la pause avec ESPACE que si le menu d'équilibrage est ouvert
                if self.balance_menu_active:
                    self.toggle_pause()
                    return True
        return False
    
    def update(self, dt: float) -> float:
        """Met à jour le système de pause et retourne le delta time ajusté."""
        if self.paused:
            return 0.0  # Pas de temps qui passe quand en pause
        return dt
    
    def draw_pause_overlay(self, surface: pygame.Surface):
        """Dessine l'overlay de pause si nécessaire."""
        if not self.paused:
            return
        
        # Créer l'overlay si nécessaire
        if self.pause_overlay is None or self.pause_overlay.get_size() != surface.get_size():
            self.pause_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            
        # Fond semi-transparent
        self.pause_overlay.fill((0, 0, 0, 100))
        surface.blit(self.pause_overlay, (0, 0))
        
        # Texte de pause
        if self.font:
            pause_text = self.font.render("⏸️ PAUSE", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
            surface.blit(pause_text, text_rect)
        
        # Instructions
        try:
            if hasattr(self, 'font_small'):
                font_small = self.font_small
            else:
                font_small = pygame.font.Font(None, 24)
        except:
            try:
                font_small = pygame.font.SysFont('Arial', 24)
            except:
                font_small = None
        
        if font_small:
            instruction_text = font_small.render("ESPACE: Reprendre | F1: Menu d'équilibrage", True, (200, 200, 200))
            instruction_rect = instruction_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 50))
            surface.blit(instruction_text, instruction_rect)

# Instance globale
pause_system = PauseSystem() 