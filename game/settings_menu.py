# game/settings_menu.py
"""
Menu de paramètres pour Death Must Pygame.
Interface graphique pour configurer le jeu.
"""

import pygame
import pygame.freetype
from typing import Dict, Any, Tuple, Optional
from .settings_manager import settings

class SettingsMenu:
    """Menu de paramètres avec interface graphique."""
    
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.active = False
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configuration de l'interface
        self.menu_width = 700
        self.menu_height = 550
        self.menu_x = (screen_width - self.menu_width) // 2
        self.menu_y = (screen_height - self.menu_height) // 2
        
        # Couleurs
        self.bg_color = (30, 30, 40, 240)
        self.panel_color = (50, 50, 60)
        self.text_color = (255, 255, 255)
        self.accent_color = (70, 130, 255)
        self.button_color = (70, 70, 80)
        self.button_hover_color = (90, 90, 100)
        self.tab_active_color = (70, 130, 255)
        
        # État de l'interface
        self.current_tab = "audio"
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        self.mouse_held = False
        self.scroll_y = 0
        self.max_scroll = 0
        
        # Onglets
        self.tabs = {
            "audio": "Audio",
            "video": "Video", 
            "hud": "Interface",
            "keybinds": "Touches"
        }
        
        # Configuration des keybinds
        self.key_names = {
            pygame.K_z: "Z", pygame.K_q: "Q", pygame.K_s: "S", pygame.K_d: "D",
            pygame.K_SPACE: "ESPACE", pygame.K_ESCAPE: "ÉCHAP", pygame.K_F1: "F1",
            pygame.K_w: "W", pygame.K_a: "A", pygame.K_e: "E", pygame.K_r: "R",
            pygame.K_t: "T", pygame.K_UP: "↑", pygame.K_DOWN: "↓", 
            pygame.K_LEFT: "←", pygame.K_RIGHT: "→",
            "mouse_left": "CLIC GAUCHE", "mouse_right": "CLIC DROIT"
        }
        
        self.waiting_for_key = None  # Action en attente d'attribution de touche
        
        # Polices
        self._init_fonts()
        
        # Variables des paramètres
        self.pending_resolution = None  # Résolution en attente de confirmation
        self.resolution_timer = 0
        
    def _init_fonts(self):
        """Initialise les polices."""
        try:
            if not pygame.font.get_init():
                pygame.font.init()
            self.font = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 20)
            self.font_title = pygame.font.Font(None, 32)
        except:
            try:
                pygame.font.init()
                self.font = pygame.font.SysFont('Arial', 24)
                self.font_small = pygame.font.SysFont('Arial', 20)
                self.font_title = pygame.font.SysFont('Arial', 32)
            except:
                self.font = None
                self.font_small = None
                self.font_title = None
    
    def toggle(self):
        """Active/désactive le menu de paramètres."""
        self.active = not self.active
        if self.active:
            print("⚙️ Menu des paramètres ouvert")
        else:
            print("⚙️ Menu des paramètres fermé")
    
    def handle_event(self, event) -> bool:
        """Gère les événements du menu."""
        if not self.active:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                return True
            elif self.waiting_for_key:
                # Attribution d'une nouvelle touche
                self._assign_key(event.key)
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
                # Sauvegarder quand on relâche la souris (fin d'ajustement slider)
                if self.current_tab == "audio" or self.current_tab == "hud":
                    settings.save_settings()
                return True
        
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            return True
        
        return True  # Absorber tous les événements
    
    def update(self, dt: float):
        """Met à jour le menu."""
        if not self.active:
            return
        
        # Timer pour confirmation de résolution
        if self.pending_resolution:
            self.resolution_timer -= dt
            if self.resolution_timer <= 0:
                self._revert_resolution()
        
        # Traitement des clics
        if self.mouse_clicked:
            self._handle_clicks()
            self.mouse_clicked = False
    
    def _handle_clicks(self):
        """Traite les clics sur l'interface."""
        # Clics sur les onglets
        tab_y = self.menu_y + 60
        tab_width = self.menu_width // len(self.tabs)
        
        for i, (tab_key, tab_name) in enumerate(self.tabs.items()):
            tab_x = self.menu_x + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 35)
            
            if self._is_point_in_rect(self.mouse_pos, tab_rect):
                self.current_tab = tab_key
                self.scroll_y = 0
                print(f"⚙️ Onglet: {tab_name}")
                return
        
        # Clics sur le contenu selon l'onglet
        content_rect = pygame.Rect(self.menu_x + 15, self.menu_y + 110, 
                                  self.menu_width - 30, self.menu_height - 130)
        
        # Traitement spécial du timer toggle dans l'onglet HUD
        if self.current_tab == "hud":
            # Calculer exactement la même position que dans _draw_hud_tab
            y_offset = content_rect.y - self.scroll_y + 20 + 50  # titre + slider
            timer_toggle = pygame.Rect(content_rect.x + 250, y_offset + 2, 60, 25)
            
            if self._is_point_in_rect(self.mouse_pos, timer_toggle):
                current = settings.get_timer_enabled()
                settings.set_timer_enabled(not current)
                print(f"⏱️ Timer: {'Activé' if not current else 'Désactivé'}")
                return
        
        # Clics sur le contenu selon l'onglet (autres cas)
        if self.current_tab == "video":
            self._handle_video_clicks(content_rect)
        elif self.current_tab == "hud":
            self._handle_hud_clicks(content_rect)
        elif self.current_tab == "keybinds":
            self._handle_keybind_clicks(content_rect)
    
    def _handle_video_clicks(self, content_rect):
        """Gère les clics dans l'onglet vidéo."""
        y_offset = content_rect.y - self.scroll_y + 50
        
        # Boutons de résolution
        for i, (width, height) in enumerate(settings.get_available_resolutions()):
            button_rect = pygame.Rect(content_rect.x + 20, y_offset + i * 35, 150, 30)
            if self._is_point_in_rect(self.mouse_pos, button_rect):
                self._change_resolution(width, height)
                break
    
    def _handle_hud_clicks(self, content_rect):
        """Gère les clics dans l'onglet HUD (autres que timer)."""
        # Le timer toggle est traité dans _handle_clicks() directement
        pass
    
    def _handle_keybind_clicks(self, content_rect):
        """Gère les clics dans l'onglet keybinds."""
        if self.waiting_for_key:
            return  # Ignore si on attend une touche
        
        y_offset = content_rect.y - self.scroll_y + 10
        actions = ["move_up", "move_down", "move_left", "move_right", 
                  "dash", "attack", "scream", "pause", "balance_menu"]
        
        for i, action in enumerate(actions):
            button_rect = pygame.Rect(content_rect.x + 250, y_offset + i * 35, 120, 30)
            if self._is_point_in_rect(self.mouse_pos, button_rect):
                self.waiting_for_key = action
                print(f"⌨️ Appuyez sur une touche pour: {action}")
                break
    
    def _change_resolution(self, width: int, height: int):
        """Change la résolution avec confirmation."""
        current_res = settings.get_resolution()
        if current_res != (width, height):
            self.pending_resolution = current_res
            self.resolution_timer = 10.0  # 10 secondes pour confirmer
            settings.set_resolution(width, height)
            print(f"🖥️ Résolution changée: {width}x{height} (10s pour confirmer)")
    
    def _revert_resolution(self):
        """Remet la résolution précédente."""
        if self.pending_resolution:
            width, height = self.pending_resolution
            settings.set_resolution(width, height)
            self.pending_resolution = None
            print(f"🖥️ Résolution restaurée: {width}x{height}")
    
    def _assign_key(self, key):
        """Assigne une nouvelle touche à une action."""
        if self.waiting_for_key:
            settings.set_keybind(self.waiting_for_key, key)
            key_name = self.key_names.get(key, f"Key_{key}")
            print(f"⌨️ {self.waiting_for_key}: {key_name}")
            self.waiting_for_key = None
    
    def draw(self, surface: pygame.Surface):
        """Dessine le menu de paramètres."""
        if not self.active:
            return
        
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
            title = self.font_title.render("PARAMETRES", True, self.text_color)
            title_x = self.menu_x + (self.menu_width - title.get_width()) // 2
            surface.blit(title, (title_x, self.menu_y + 15))
        
        # Instructions uniquement pour la configuration des touches
        if self.font_small and self.waiting_for_key:
            instruction = "Appuyez sur une touche ou ECHAP pour annuler"
            color = (255, 255, 100)
            inst_surface = self.font_small.render(instruction, True, color)
            inst_x = self.menu_x + (self.menu_width - inst_surface.get_width()) // 2
            surface.blit(inst_surface, (inst_x, self.menu_y + 50))
        
        # Onglets
        self._draw_tabs(surface)
        
        # Contenu
        content_rect = pygame.Rect(self.menu_x + 15, self.menu_y + 110, 
                                  self.menu_width - 30, self.menu_height - 130)
        pygame.draw.rect(surface, (40, 40, 50), content_rect)
        
        # Dessiner le contenu avec clipping
        surface.set_clip(content_rect)
        if self.current_tab == "audio":
            self._draw_audio_tab(surface, content_rect)
        elif self.current_tab == "video":
            self._draw_video_tab(surface, content_rect)
        elif self.current_tab == "hud":
            self._draw_hud_tab(surface, content_rect)
        elif self.current_tab == "keybinds":
            self._draw_keybinds_tab(surface, content_rect)
        surface.set_clip(None)
        
        # Message de confirmation résolution
        if self.pending_resolution:
            self._draw_resolution_confirmation(surface)
    
    def _draw_tabs(self, surface: pygame.Surface):
        """Dessine les onglets."""
        tab_y = self.menu_y + 60
        tab_width = self.menu_width // len(self.tabs)
        
        for i, (tab_key, tab_name) in enumerate(self.tabs.items()):
            tab_x = self.menu_x + i * tab_width
            tab_rect = pygame.Rect(tab_x, tab_y, tab_width, 35)
            
            # Couleur de l'onglet
            if tab_key == self.current_tab:
                tab_color = self.tab_active_color
            elif self._is_point_in_rect(self.mouse_pos, tab_rect):
                tab_color = self.button_hover_color
            else:
                tab_color = self.button_color
            
            pygame.draw.rect(surface, tab_color, tab_rect)
            pygame.draw.rect(surface, self.text_color, tab_rect, 1)
            
            # Texte de l'onglet
            if self.font_small:
                text = self.font_small.render(tab_name, True, self.text_color)
                text_x = tab_x + (tab_width - text.get_width()) // 2
                text_y = tab_y + (35 - text.get_height()) // 2
                surface.blit(text, (text_x, text_y))
    
    def _draw_audio_tab(self, surface: pygame.Surface, content_rect: pygame.Rect):
        """Dessine l'onglet audio."""
        y_offset = content_rect.y - self.scroll_y + 20
        
        if self.font:
            # Volume principal
            title = self.font.render("Volume Principal", True, self.text_color)
            surface.blit(title, (content_rect.x + 20, y_offset))
            
            # Slider de volume principal avec application temps réel
            slider_rect = pygame.Rect(content_rect.x + 200, y_offset + 5, 200, 20)
            self._draw_slider(surface, slider_rect, settings.get_master_volume(), 
                            lambda v: self._set_master_volume_realtime(v))
            
            # Valeur affichée
            vol_text = f"{int(settings.get_master_volume() * 100)}%"
            vol_surface = self.font.render(vol_text, True, self.accent_color)
            surface.blit(vol_surface, (content_rect.x + 420, y_offset))
            
            y_offset += 40
            
            # Volume musique
            music_title = self.font.render("Volume Musique", True, self.text_color)
            surface.blit(music_title, (content_rect.x + 20, y_offset))
            
            music_slider_rect = pygame.Rect(content_rect.x + 200, y_offset + 5, 200, 20)
            self._draw_slider(surface, music_slider_rect, settings.get_music_volume(), 
                            lambda v: self._set_music_volume_realtime(v))
            
            music_vol_text = f"{int(settings.get_music_volume() * 100)}%"
            music_vol_surface = self.font.render(music_vol_text, True, self.accent_color)
            surface.blit(music_vol_surface, (content_rect.x + 420, y_offset))
            
            y_offset += 40
            
            # Volume effets sonores
            sfx_title = self.font.render("Volume Effets", True, self.text_color)
            surface.blit(sfx_title, (content_rect.x + 20, y_offset))
            
            sfx_slider_rect = pygame.Rect(content_rect.x + 200, y_offset + 5, 200, 20)
            self._draw_slider(surface, sfx_slider_rect, settings.get_sfx_volume(), 
                            lambda v: self._set_sfx_volume_realtime(v))
            
            sfx_vol_text = f"{int(settings.get_sfx_volume() * 100)}%"
            sfx_vol_surface = self.font.render(sfx_vol_text, True, self.accent_color)
            surface.blit(sfx_vol_surface, (content_rect.x + 420, y_offset))
    
    def _set_master_volume_realtime(self, volume):
        """Applique le volume principal en temps réel sans sauvegarde immédiate."""
        settings.set_master_volume(volume, auto_save=False)
    
    def _set_music_volume_realtime(self, volume):
        """Applique le volume musique en temps réel sans sauvegarde immédiate."""
        settings.set_music_volume(volume, auto_save=False)
    
    def _set_sfx_volume_realtime(self, volume):
        """Applique le volume effets sonores en temps réel sans sauvegarde immédiate."""
        settings.set_sfx_volume(volume, auto_save=False)
    
    def _draw_video_tab(self, surface: pygame.Surface, content_rect: pygame.Rect):
        """Dessine l'onglet vidéo."""
        y_offset = content_rect.y - self.scroll_y + 20
        
        if self.font:
            # Titre résolution
            title = self.font.render("Resolution", True, self.text_color)
            surface.blit(title, (content_rect.x + 20, y_offset))
            y_offset += 30
            
            # Résolution actuelle
            current_res = settings.get_resolution()
            current_text = f"Actuelle: {current_res[0]}x{current_res[1]}"
            current_surface = self.font_small.render(current_text, True, (200, 200, 200))
            surface.blit(current_surface, (content_rect.x + 20, y_offset))
            y_offset += 20
            
            # Boutons de résolution
            for i, (width, height) in enumerate(settings.get_available_resolutions()):
                button_rect = pygame.Rect(content_rect.x + 20, y_offset + i * 35, 150, 30)
                
                # Couleur selon état
                is_current = (width, height) == current_res
                if is_current:
                    button_color = self.accent_color
                elif self._is_point_in_rect(self.mouse_pos, button_rect):
                    button_color = self.button_hover_color
                else:
                    button_color = self.button_color
                
                pygame.draw.rect(surface, button_color, button_rect)
                pygame.draw.rect(surface, self.text_color, button_rect, 1)
                
                # Texte du bouton
                res_text = f"{width}x{height}"
                if self.font_small:
                    text_surface = self.font_small.render(res_text, True, self.text_color)
                    text_x = button_rect.x + (button_rect.width - text_surface.get_width()) // 2
                    text_y = button_rect.y + (button_rect.height - text_surface.get_height()) // 2
                    surface.blit(text_surface, (text_x, text_y))
    
    def _draw_hud_tab(self, surface: pygame.Surface, content_rect: pygame.Rect):
        """Dessine l'onglet HUD."""
        y_offset = content_rect.y - self.scroll_y + 20
        
        if self.font:
            # Échelle HUD
            title = self.font.render("Taille de l'interface", True, self.text_color)
            surface.blit(title, (content_rect.x + 20, y_offset))
            
            slider_rect = pygame.Rect(content_rect.x + 250, y_offset + 5, 200, 20)
            self._draw_slider(surface, slider_rect, 
                            (settings.get_hud_scale() - 0.5) / 1.5,  # 0.5-2.0 -> 0-1
                            lambda v: settings.set_hud_scale(0.5 + v * 1.5, auto_save=False))
            
            scale_text = f"{settings.get_hud_scale():.1f}x"
            scale_surface = self.font.render(scale_text, True, self.accent_color)
            surface.blit(scale_surface, (content_rect.x + 470, y_offset))
            
            y_offset += 50
            
            # Toggle timer avec position et logique corrigée
            timer_title = self.font.render("Afficher le timer", True, self.text_color)
            surface.blit(timer_title, (content_rect.x + 20, y_offset))
            
            toggle_rect = pygame.Rect(content_rect.x + 250, y_offset + 2, 60, 25)
            enabled = settings.get_timer_enabled()
            self._draw_toggle(surface, toggle_rect, enabled)
    
    def _draw_keybinds_tab(self, surface: pygame.Surface, content_rect: pygame.Rect):
        """Dessine l'onglet des touches."""
        y_offset = content_rect.y - self.scroll_y + 10
        
        action_names = {
            "move_up": "Avancer",
            "move_down": "Reculer", 
            "move_left": "Gauche",
            "move_right": "Droite",
            "dash": "Dash",
            "attack": "Attaque",
            "scream": "Cri",
            "pause": "Pause",
            "balance_menu": "Equilibrage"
        }
        
        for action, display_name in action_names.items():
            if self.font:
                # Nom de l'action
                name_surface = self.font.render(display_name, True, self.text_color)
                surface.blit(name_surface, (content_rect.x + 20, y_offset))
                
                # Bouton de la touche
                button_rect = pygame.Rect(content_rect.x + 250, y_offset, 120, 30)
                
                if self.waiting_for_key == action:
                    button_color = (255, 255, 100)
                    key_text = "..."
                elif self._is_point_in_rect(self.mouse_pos, button_rect):
                    button_color = self.button_hover_color
                    key = settings.get_keybind(action)
                    key_text = self.key_names.get(key, f"Key_{key}")
                else:
                    button_color = self.button_color
                    key = settings.get_keybind(action)
                    key_text = self.key_names.get(key, f"Key_{key}")
                
                pygame.draw.rect(surface, button_color, button_rect)
                pygame.draw.rect(surface, self.text_color, button_rect, 1)
                
                # Texte de la touche
                if self.font_small:
                    key_surface = self.font_small.render(key_text, True, self.text_color)
                    text_x = button_rect.x + (button_rect.width - key_surface.get_width()) // 2
                    text_y = button_rect.y + (button_rect.height - key_surface.get_height()) // 2
                    surface.blit(key_surface, (text_x, text_y))
            
            y_offset += 35
    
    def _draw_slider(self, surface: pygame.Surface, rect: pygame.Rect, 
                    value: float, callback):
        """Dessine un slider horizontal."""
        # Fond du slider
        pygame.draw.rect(surface, (60, 60, 70), rect)
        pygame.draw.rect(surface, self.text_color, rect, 1)
        
        # Curseur
        cursor_x = rect.x + value * (rect.width - 10)
        cursor_rect = pygame.Rect(cursor_x, rect.y, 10, rect.height)
        pygame.draw.rect(surface, self.accent_color, cursor_rect)
        
        # Interaction
        if self._is_point_in_rect(self.mouse_pos, rect) and self.mouse_held:
            mouse_x = self.mouse_pos[0] - rect.x
            ratio = max(0, min(1, mouse_x / rect.width))
            callback(ratio)
    
    def _draw_toggle(self, surface: pygame.Surface, rect: pygame.Rect, enabled: bool):
        """Dessine un bouton toggle."""
        color = (100, 200, 100) if enabled else (200, 100, 100)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, self.text_color, rect, 1)
        
        if self.font_small:
            text = "ON" if enabled else "OFF"
            text_surface = self.font_small.render(text, True, self.text_color)
            text_x = rect.x + (rect.width - text_surface.get_width()) // 2
            text_y = rect.y + (rect.height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
    
    def _draw_resolution_confirmation(self, surface: pygame.Surface):
        """Dessine le message de confirmation de résolution."""
        if self.font:
            text = f"Nouvelle résolution appliquée. Retour automatique dans {self.resolution_timer:.0f}s"
            text_surface = self.font.render(text, True, (255, 255, 100))
            text_x = (self.screen_width - text_surface.get_width()) // 2
            text_y = self.screen_height - 50
            
            # Fond pour le texte
            bg_rect = pygame.Rect(text_x - 10, text_y - 5, 
                                text_surface.get_width() + 20, 
                                text_surface.get_height() + 10)
            pygame.draw.rect(surface, (40, 40, 50), bg_rect)
            pygame.draw.rect(surface, (255, 255, 100), bg_rect, 2)
            
            surface.blit(text_surface, (text_x, text_y))
    
    def _is_point_in_rect(self, point: Tuple[int, int], rect: pygame.Rect) -> bool:
        """Vérifie si un point est dans un rectangle."""
        return rect.collidepoint(point) 