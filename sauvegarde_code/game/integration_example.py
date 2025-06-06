#!/usr/bin/env python3
"""
Exemple d'intégration du menu d'équilibrage in-game.
Montre comment l'ajouter à votre jeu pygame existant.
"""

import pygame
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent.parent))

from game.balance_menu import BalanceMenu
from game.pause_system import pause_system
from game.balance_manager import balance

class GameWithBalanceMenu:
    """Exemple d'intégration du menu d'équilibrage."""
    
    def __init__(self):
        pygame.init()
        
        # Configuration de l'écran
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Death Must Pygame - Avec Menu d'Équilibrage")
        
        # Horloge pour les FPS
        self.clock = pygame.time.Clock()
        self.dt = 0
        
        # Menu d'équilibrage
        self.balance_menu = BalanceMenu(self.screen_width, self.screen_height)
        
        # Variables de jeu pour démonstration
        self.player_pos = [self.screen_width // 2, self.screen_height // 2]
        self.enemies = []
        self.font = pygame.font.Font(None, 36)
        
        # État du jeu
        self.running = True
        
        print("🎮 Jeu avec menu d'équilibrage initialisé!")
        print("📋 CONTRÔLES:")
        print("   F1: Ouvrir/fermer le menu d'équilibrage")
        print("   ESPACE: Pause/reprendre")
        print("   ÉCHAP: Quitter")
    
    def handle_events(self):
        """Gère tous les événements du jeu."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F1:
                    # Toggle du menu d'équilibrage
                    self.balance_menu.toggle()
                    # Mettre en pause automatiquement quand le menu s'ouvre
                    if self.balance_menu.active:
                        pause_system.pause()
                    else:
                        pause_system.resume()
            
            # Laisser le système de pause gérer ses événements
            if not self.balance_menu.active:
                pause_system.handle_event(event)
            
            # Laisser le menu d'équilibrage gérer ses événements
            # Important: le menu absorbe les événements quand il est actif
            if self.balance_menu.handle_event(event):
                continue  # Événement absorbé par le menu
    
    def update(self):
        """Met à jour la logique du jeu."""
        # Appliquer la pause - si en pause, dt sera 0
        adjusted_dt = pause_system.update(self.dt)
        
        if adjusted_dt > 0:  # Seulement mettre à jour si pas en pause
            # Exemple de logique de jeu utilisant les stats d'équilibrage
            
            # Récupérer les stats du joueur depuis le balance manager
            player_speed = balance.get_player_stats().get("speed", 150)
            
            # Déplacement du joueur avec les flèches
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player_pos[0] -= player_speed * adjusted_dt
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player_pos[0] += player_speed * adjusted_dt
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player_pos[1] -= player_speed * adjusted_dt
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player_pos[1] += player_speed * adjusted_dt
            
            # Garder le joueur à l'écran
            self.player_pos[0] = max(25, min(self.screen_width - 25, self.player_pos[0]))
            self.player_pos[1] = max(25, min(self.screen_height - 25, self.player_pos[1]))
        
        # Mettre à jour le menu d'équilibrage
        self.balance_menu.update(adjusted_dt)
    
    def draw(self):
        """Dessine tout le jeu."""
        # Fond
        self.screen.fill((20, 30, 40))
        
        # Afficher les stats actuelles pour démonstration
        self._draw_stats_demo()
        
        # Dessiner le joueur
        player_color = (100, 150, 255)
        pygame.draw.circle(self.screen, player_color, 
                         (int(self.player_pos[0]), int(self.player_pos[1])), 25)
        
        # Overlay de pause
        pause_system.draw_pause_overlay(self.screen)
        
        # Menu d'équilibrage (dessiné en dernier pour être au-dessus)
        self.balance_menu.draw(self.screen)
        
        # Instructions
        if not self.balance_menu.active:
            self._draw_instructions()
        
        pygame.display.flip()
    
    def _draw_stats_demo(self):
        """Affiche les stats actuelles pour démonstration."""
        y_offset = 10
        
        # Stats du joueur
        player_stats = balance.get_player_stats()
        stats_text = [
            f"👤 Joueur - Vitesse: {player_stats.get('speed', 'N/A')}",
            f"           Dégâts: {player_stats.get('attack_damage', 'N/A')}",
            f"           HP: {player_stats.get('max_hp', 'N/A')}",
            f"🎯 Difficulté: {balance.difficulty_level}",
        ]
        
        for text in stats_text:
            text_surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 30
    
    def _draw_instructions(self):
        """Affiche les instructions de contrôle."""
        instructions = [
            "F1: Menu d'équilibrage",
            "ESPACE: Pause",
            "WASD/Flèches: Déplacer"
        ]
        
        y_offset = self.screen_height - len(instructions) * 25 - 10
        font_small = pygame.font.Font(None, 20)
        
        for instruction in instructions:
            text_surface = font_small.render(instruction, True, (200, 200, 200))
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 25
    
    def run(self):
        """Boucle principale du jeu."""
        print("🚀 Lancement du jeu avec menu d'équilibrage...")
        
        while self.running:
            # Calculer delta time
            self.dt = self.clock.tick(60) / 1000.0
            
            # Gérer les événements
            self.handle_events()
            
            # Mettre à jour le jeu
            self.update()
            
            # Dessiner le jeu
            self.draw()
        
        print("👋 Fermeture du jeu")
        pygame.quit()

def main():
    """Point d'entrée principal."""
    try:
        game = GameWithBalanceMenu()
        game.run()
    except KeyboardInterrupt:
        print("\n👋 Jeu interrompu par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main() 