# game/balance_menu.py
"""
Menu d'équilibrage in-game pour Death Must Pygame.
Interface simple pour modifier les paramètres en temps réel.
"""

import pygame
import math
from typing import Dict, Any, Callable, Tuple
from .balance_manager import balance

class BalanceMenu:
    """Menu d'équilibrage accessible en jeu avec la touche F1."""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.active = False
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configuration de l'interface
        self.menu_width = 600
        self.menu_height = 500
        self.menu_x = (screen_width - self.menu_width) // 2
        self.menu_y = (screen_height - self.menu_height) // 2
        
        # Couleurs
        self.bg_color = (40, 40, 50, 200)  # Fond semi-transparent
        self.panel_color = (60, 60, 70)
        self.text_color = (255, 255, 255)
        self.accent_color = (100, 150, 255)
        self.button_color = (80, 80, 90)
        self.button_hover_color = (100, 100, 110)
        
        # Police
        try:
            # S'assurer que pygame.font est initialisé
            if not pygame.get_init():
                pygame.init()
            if not pygame.font.get_init():
                pygame.font.init()
            self.font = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
            self.font_title = pygame.font.Font(None, 32)
        except:
            try:
                pygame.font.init()
                self.font = pygame.font.SysFont('Arial', 24)
                self.font_small = pygame.font.SysFont('Arial', 18)
                self.font_title = pygame.font.SysFont('Arial', 32)
            except:
                # Polices par défaut minimales
                self.font = None
                self.font_small = None
                self.font_title = None
        
        # État de l'interface
        self.scroll_y = 0
        self.max_scroll = 0
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        self.mouse_held = False
        
        # Onglets
        self.current_tab = "player"
        self.tabs = {
            "player": "👤 Joueur",
            "enemies": "👹 Ennemis", 
            "difficulty": "🎯 Difficulté",
            "spawning": "🌊 Spawn",
            "scaling": "📈 Scaling",
            "upgrades": "⭐ Améliorations"
        }
        
        # CORRECTION: Variables modifiables mises à jour selon la vraie structure JSON
        self.variables = {
            "player": {
                "attack_damage": {"name": "Dégâts", "min": 1, "max": 20, "step": 0.5, "type": float},
                "max_hp": {"name": "HP Max", "min": 5, "max": 100, "step": 5, "type": int},
                "speed": {"name": "Vitesse", "min": 50, "max": 400, "step": 10, "type": int},
                "attack_range": {"name": "Portée", "min": 50, "max": 500, "step": 10, "type": int},
                "attack_cooldown": {"name": "Cooldown", "min": 0.1, "max": 5.0, "step": 0.1, "type": float},
                "dash.speed": {"name": "Vitesse Dash", "min": 200, "max": 1500, "step": 50, "type": int},
                "dash.cooldown": {"name": "Cooldown Dash", "min": 1.0, "max": 10.0, "step": 0.5, "type": float},
                "scream.damage": {"name": "Dégâts Cri", "min": 1, "max": 20, "step": 1, "type": int},
                "scream.cooldown": {"name": "Cooldown Cri", "min": 1.0, "max": 30.0, "step": 1.0, "type": float}
            },
            "enemies": {
                "normal.hp": {"name": "HP Normal", "min": 5, "max": 100, "step": 5, "type": int},
                "normal.speed": {"name": "Vitesse Normal", "min": 20, "max": 200, "step": 10, "type": int},
                "normal.damage": {"name": "Dégâts Normal", "min": 1, "max": 10, "step": 1, "type": int},
                "normal.xp_value": {"name": "XP Normal", "min": 5, "max": 50, "step": 5, "type": int},
                "goblin_mage.hp": {"name": "HP Mage", "min": 5, "max": 80, "step": 5, "type": int},
                "goblin_mage.speed": {"name": "Vitesse Mage", "min": 20, "max": 150, "step": 10, "type": int},
                "goblin_mage.damage": {"name": "Dégâts Mage", "min": 1, "max": 15, "step": 1, "type": int},
                "boss.hp": {"name": "HP Boss", "min": 50, "max": 500, "step": 25, "type": int},
                "boss.damage": {"name": "Dégâts Boss", "min": 5, "max": 50, "step": 5, "type": int}
            },
            "spawning": {
                "base_spawn_rate": {"name": "Taux Spawn", "min": 0.1, "max": 5.0, "step": 0.1, "type": float},
                "max_enemies": {"name": "Max Ennemis", "min": 10, "max": 200, "step": 10, "type": int},
                "spawn_distance_min": {"name": "Distance Min", "min": 100, "max": 500, "step": 25, "type": int},
                "spawn_distance_max": {"name": "Distance Max", "min": 200, "max": 800, "step": 50, "type": int},
                "base_max_enemies": {"name": "Base Max Ennemis", "min": 1, "max": 20, "step": 1, "type": int},
                "per_level_enemies": {"name": "Ennemis/Niveau", "min": 1, "max": 10, "step": 1, "type": int},
                "mage_spawn_chance": {"name": "Chance Mage", "min": 0.0, "max": 1.0, "step": 0.05, "type": float}
            },
            "scaling": {
                "enemy_tier_chances.elite_chance_per_level": {"name": "Elite/Niveau", "min": 0.001, "max": 0.02, "step": 0.001, "type": float},
                "enemy_tier_chances.elite_chance_max": {"name": "Elite Max", "min": 0.05, "max": 0.5, "step": 0.05, "type": float},
                "enemy_tier_chances.rare_chance_per_level": {"name": "Rare/Niveau", "min": 0.005, "max": 0.05, "step": 0.005, "type": float},
                "enemy_tier_chances.rare_chance_max": {"name": "Rare Max", "min": 0.1, "max": 0.8, "step": 0.1, "type": float},
                "time_scaling.time_modifier_divisor": {"name": "Diviseur Temps", "min": 30, "max": 120, "step": 10, "type": int},
                "time_scaling.level_modifier_per_level": {"name": "Mod Niveau", "min": 0.005, "max": 0.02, "step": 0.005, "type": float},
                "enemy_progression.hp_per_level": {"name": "HP/Niveau", "min": 1, "max": 10, "step": 1, "type": int},
                "enemy_progression.speed_per_level": {"name": "Vitesse/Niveau", "min": 1, "max": 20, "step": 1, "type": int},
                "enemy_progression.elite_hp_multiplier": {"name": "x HP Elite", "min": 2.0, "max": 20.0, "step": 1.0, "type": float},
                "enemy_progression.rare_hp_multiplier": {"name": "x HP Rare", "min": 1.5, "max": 10.0, "step": 0.5, "type": float}
            },
            "upgrades": {
                "strength_boost.value": {"name": "Force +", "min": 1, "max": 10, "step": 1, "type": int},
                "vitality_surge.value": {"name": "Vitalité +", "min": 1, "max": 20, "step": 1, "type": int},
                "quick_reflexes.value": {"name": "Reflexes x", "min": 0.5, "max": 0.95, "step": 0.05, "type": float},
                "haste.value": {"name": "Hâte +", "min": 10, "max": 100, "step": 10, "type": int},
                "extended_reach.value": {"name": "Portée +", "min": 10, "max": 100, "step": 10, "type": int},
                "xp_bonus.value": {"name": "Bonus XP +", "min": 0.1, "max": 1.0, "step": 0.05, "type": float}
            }
        }
    
    def toggle(self):
        """Active/désactive le menu d'équilibrage."""
        self.active = not self.active
        
        # CORRECTION: Informer le système de pause de l'état du menu
        from .pause_system import pause_system
        pause_system.set_balance_menu_active(self.active)
        
        if self.active:
            print("🎮 Menu d'équilibrage activé (F1 pour fermer)")
        else:
            print("🎮 Menu d'équilibrage fermé")
    
    def handle_event(self, event):
        """Gère les événements du menu."""
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.toggle()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                # CORRECTION: Informer le système de pause
                from .pause_system import pause_system
                pause_system.set_balance_menu_active(False)
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                self.mouse_clicked = True
                self.mouse_held = True
                return True
            elif event.button == 4:  # Molette haut
                self.scroll_y = max(0, self.scroll_y - 30)
                return True
            elif event.button == 5:  # Molette bas
                self.scroll_y = min(self.max_scroll, self.scroll_y + 30)
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_held = False
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            return True
        
        return True  # Absorber tous les événements quand le menu est actif
    
    def update(self, dt: float):
        """Met à jour le menu."""
        if not self.active:
            return
        
        # CORRECTION: Traiter les clics sur les onglets AVANT de remettre mouse_clicked à False
        if self.mouse_clicked:
            # Vérifier les clics sur les onglets
            tab_y = self.menu_y + 70
            tab_width = self.menu_width // len(self.tabs)
            
            for i, (tab_key, tab_name) in enumerate(self.tabs.items()):
                tab_x = self.menu_x + i * tab_width
                tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 30)
                
                if self._is_point_in_rect(self.mouse_pos, tab_rect):
                    self.current_tab = tab_key
                    self.scroll_y = 0
                    print(f"🎮 Onglet changé: {tab_name}")
                    break
        
        # Reset du clic APRÈS traitement
        if self.mouse_clicked:
            self.mouse_clicked = False
    
    def draw(self, surface: pygame.Surface):
        """Dessine le menu d'équilibrage."""
        if not self.active:
            return
        
        # Vérifier que au moins une police est disponible
        if not self.font and not self.font_small and not self.font_title:
            # Essayer de réinitialiser les polices
            try:
                pygame.font.init()
                self.font = pygame.font.SysFont('Arial', 24)
                self.font_small = pygame.font.SysFont('Arial', 18)
                self.font_title = pygame.font.SysFont('Arial', 32)
            except:
                # Si vraiment aucune police ne fonctionne, afficher au moins le fond
                pass
        
        # Fond semi-transparent
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        surface.blit(overlay, (0, 0))
        
        # Panel principal
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(surface, self.panel_color, menu_rect)
        pygame.draw.rect(surface, self.accent_color, menu_rect, 2)
        
        # Titre
        if self.font_title:
            title_text = self.font_title.render("🎮 ÉQUILIBRAGE EN TEMPS RÉEL", True, self.text_color)
            title_x = self.menu_x + (self.menu_width - title_text.get_width()) // 2
            surface.blit(title_text, (title_x, self.menu_y + 10))
        
        # Instructions
        if self.font_small:
            instruction = self.font_small.render("F1: Fermer | Molette: Défiler | Clic: Modifier", True, (200, 200, 200))
            instruction_x = self.menu_x + (self.menu_width - instruction.get_width()) // 2
            surface.blit(instruction, (instruction_x, self.menu_y + 40))
        
        # Onglets
        tab_y = self.menu_y + 70
        tab_width = self.menu_width // len(self.tabs)
        
        for i, (tab_key, tab_name) in enumerate(self.tabs.items()):
            tab_x = self.menu_x + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 30)
            
            # CORRECTION: Simplifier - juste l'affichage et hover, pas de clic (géré dans update())
            tab_color = self.accent_color if tab_key == self.current_tab else self.button_color
            if self._is_point_in_rect(self.mouse_pos, tab_rect):
                tab_color = self.button_hover_color
            
            pygame.draw.rect(surface, tab_color, tab_rect)
            pygame.draw.rect(surface, self.text_color, tab_rect, 1)
            
            # Texte de l'onglet
            if self.font_small:
                tab_text = self.font_small.render(tab_name, True, self.text_color)
                text_x = tab_x + (tab_width - tab_text.get_width()) // 2
                text_y = tab_y + (30 - tab_text.get_height()) // 2
                surface.blit(tab_text, (text_x, text_y))
        
        # Zone de contenu
        content_rect = pygame.Rect(self.menu_x + 10, self.menu_y + 110, 
                                  self.menu_width - 20, self.menu_height - 120)
        pygame.draw.rect(surface, (50, 50, 60), content_rect)
        
        # Contenu des onglets avec clipping
        surface.set_clip(content_rect)
        self._draw_tab_content(surface, content_rect)
        surface.set_clip(None)
        
        # Barre de sauvegarde
        if self.font_small:
            save_text = self.font_small.render("💾 Sauvegarde automatique", True, (100, 255, 100))
            surface.blit(save_text, (self.menu_x + 10, self.menu_y + self.menu_height - 25))
    
    def _draw_tab_content(self, surface: pygame.Surface, content_rect: pygame.Rect):
        """Dessine le contenu de l'onglet actuel."""
        y_offset = content_rect.y - self.scroll_y + 10
        line_height = 35
        
        if self.current_tab == "difficulty":
            self._draw_difficulty_tab(surface, content_rect, y_offset, line_height)
        else:
            # CORRECTION: Utiliser le bon dictionnaire de variables
            variables = self.variables.get(self.current_tab, {})
            
            if not variables:
                # Afficher un message si aucune variable n'est trouvée
                if self.font:
                    no_vars_text = self.font.render(f"Aucune variable pour l'onglet '{self.current_tab}'", True, self.text_color)
                    surface.blit(no_vars_text, (content_rect.x + 10, y_offset))
                return
            
            for var_path, var_info in variables.items():
                if y_offset > content_rect.bottom + 50:  # Optimisation: ne pas dessiner hors écran
                    break
                if y_offset > content_rect.y - 50:  # Optimisation: commencer à dessiner proche de l'écran
                    self._draw_variable_slider(surface, content_rect, var_path, var_info, y_offset)
                y_offset += line_height
        
        # Calculer le scroll maximum
        if self.current_tab == "difficulty":
            total_height = len(balance.config.get("difficulty", {})) * 50 + 100
        else:
            total_height = len(self.variables.get(self.current_tab, {})) * line_height
        self.max_scroll = max(0, total_height - content_rect.height + 20)
    
    def _draw_difficulty_tab(self, surface: pygame.Surface, content_rect: pygame.Rect, y_offset: int, line_height: int):
        """Dessine l'onglet de sélection de difficulté."""
        difficulties = balance.config.get("difficulty", {})
        current_difficulty = balance.difficulty_level
        
        # Titre
        if self.font:
            title = self.font.render("🎯 Niveau de difficulté:", True, self.text_color)
            surface.blit(title, (content_rect.x + 10, y_offset))
        y_offset += 40
        
        # Boutons de difficulté
        for diff_name, diff_data in difficulties.items():
            button_rect = pygame.Rect(content_rect.x + 20, y_offset, content_rect.width - 40, 30)
            
            # Couleur du bouton
            if diff_name == current_difficulty:
                button_color = self.accent_color
            elif self._is_point_in_rect(self.mouse_pos, button_rect):
                button_color = self.button_hover_color
                if self.mouse_clicked:
                    balance.set_difficulty(diff_name)
                    print(f"🎯 Difficulté changée: {diff_name}")
            else:
                button_color = self.button_color
            
            pygame.draw.rect(surface, button_color, button_rect)
            pygame.draw.rect(surface, self.text_color, button_rect, 1)
            
            # Texte du bouton
            multipliers = diff_data
            button_text = f"{diff_name.upper()} - HP: x{multipliers.get('hp_multiplier', 1.0):.1f}, Dmg: x{multipliers.get('damage_multiplier', 1.0):.1f}"
            if self.font_small:
                text_surface = self.font_small.render(button_text, True, self.text_color)
                text_x = button_rect.x + 10
                text_y = button_rect.y + (button_rect.height - text_surface.get_height()) // 2
                surface.blit(text_surface, (text_x, text_y))
            
            y_offset += 40
    
    def _draw_variable_slider(self, surface: pygame.Surface, content_rect: pygame.Rect, 
                            var_path: str, var_info: Dict[str, Any], y_offset: int):
        """Dessine un slider pour une variable."""
        # CORRECTION: Construire le chemin correct selon l'onglet
        if self.current_tab == "player":
            full_path = f"player.{var_path}"
        elif self.current_tab == "enemies":
            full_path = f"enemies.{var_path}"
        elif self.current_tab == "spawning":
            full_path = f"spawning.{var_path}"
        elif self.current_tab == "scaling":
            full_path = f"scaling.{var_path}"
        elif self.current_tab == "upgrades":
            full_path = f"upgrades.{var_path}"
        else:
            full_path = var_path
        
        # Récupérer la valeur actuelle
        current_value = balance.get_value(full_path, var_info.get("min", 0))
        
        # Nom de la variable
        if self.font:
            name_text = self.font.render(var_info["name"], True, self.text_color)
            surface.blit(name_text, (content_rect.x + 10, y_offset))
        
        # Valeur actuelle
        value_text = f"{current_value}"
        if var_info["type"] == float:
            value_text = f"{current_value:.1f}"
        if self.font:
            value_surface = self.font.render(value_text, True, self.accent_color)
            surface.blit(value_surface, (content_rect.x + content_rect.width - 80, y_offset))
        
        # Slider
        slider_rect = pygame.Rect(content_rect.x + 150, y_offset + 5, 200, 20)
        pygame.draw.rect(surface, (30, 30, 40), slider_rect)
        pygame.draw.rect(surface, self.text_color, slider_rect, 1)
        
        # Position du curseur
        min_val = var_info["min"]
        max_val = var_info["max"]
        if max_val > min_val:
            ratio = (current_value - min_val) / (max_val - min_val)
            cursor_x = slider_rect.x + ratio * (slider_rect.width - 10)
            cursor_rect = pygame.Rect(cursor_x, slider_rect.y, 10, slider_rect.height)
            pygame.draw.rect(surface, self.accent_color, cursor_rect)
        
        # Interaction avec le slider
        if self._is_point_in_rect(self.mouse_pos, slider_rect) and self.mouse_held:
            # Calculer la nouvelle valeur
            mouse_x = self.mouse_pos[0] - slider_rect.x
            ratio = max(0, min(1, mouse_x / slider_rect.width))
            new_value = min_val + ratio * (max_val - min_val)
            
            # Arrondir selon le step
            step = var_info.get("step", 1)
            new_value = round(new_value / step) * step
            new_value = var_info["type"](new_value)
            
            # Appliquer la nouvelle valeur avec le bon chemin
            balance.set_value(full_path, new_value)
            
            # Sauvegarder automatiquement
            balance.save_config()
    
    def _is_point_in_rect(self, point: Tuple[int, int], rect: pygame.Rect) -> bool:
        """Vérifie si un point est dans un rectangle."""
        return rect.collidepoint(point) 