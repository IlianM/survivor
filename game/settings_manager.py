"""
Gestionnaire de paramètres pour Death Must Pygame.
Gère la sauvegarde et le chargement des préférences utilisateur.
"""

import json
import os
import pygame
from typing import Dict, Any, Tuple, List

class SettingsManager:
    """Gestionnaire central des paramètres du jeu."""
    
    def __init__(self):
        self.settings_file = "config/game_settings.json"
        self.settings = {}
        
        # Paramètres par défaut
        self.default_settings = {
            "audio": {
                "master_volume": 0.7,
                "music_volume": 0.5,
                "sfx_volume": 0.8
            },
            "video": {
                "resolution": [800, 600],
                "fullscreen": False,
                "vsync": True
            },
            "hud": {
                "scale": 1.0,
                "show_fps": False,
                "show_timer": True
            },
            "keybinds": {
                "move_up": pygame.K_z,
                "move_down": pygame.K_s, 
                "move_left": pygame.K_q,
                "move_right": pygame.K_d,
                "dash": pygame.K_SPACE,
                "attack": "mouse_left",
                "scream": "mouse_right",
                "pause": pygame.K_ESCAPE,
                "balance_menu": pygame.K_F1
            },
            "gameplay": {
                "auto_pause_on_focus_loss": True,
                "auto_pickup": True,
                "show_damage_numbers": True
            }
        }
        
        # Résolutions disponibles
        self.available_resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1366, 768),
            (1600, 900),
            (1920, 1080),
            (2560, 1440)
        ]
        
        # Créer le dossier config si nécessaire
        os.makedirs("config", exist_ok=True)
        
        # Charger les paramètres
        self.load_settings()
    
    def load_settings(self):
        """Charge les paramètres depuis le fichier JSON."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Fusionner avec les paramètres par défaut
                self.settings = self._merge_settings(self.default_settings, loaded_settings)
                print(f"✅ Paramètres chargés: {self.settings_file}")
            else:
                self.settings = self.default_settings.copy()
                self.save_settings()
                print(f"✅ Paramètres par défaut créés: {self.settings_file}")
        except Exception as e:
            print(f"⚠️ Erreur lors du chargement des paramètres: {e}")
            self.settings = self.default_settings.copy()
    
    def save_settings(self):
        """Sauvegarde les paramètres dans le fichier JSON."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"💾 Paramètres sauvegardés: {self.settings_file}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
    
    def _merge_settings(self, default: Dict, loaded: Dict) -> Dict:
        """Fusionne les paramètres chargés avec les valeurs par défaut."""
        result = default.copy()
        for key, value in loaded.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self._merge_settings(result[key], value)
                else:
                    result[key] = value
        return result
    
    def get(self, path: str, default=None):
        """Récupère une valeur de paramètre par son chemin (ex: 'audio.master_volume')."""
        try:
            keys = path.split('.')
            value = self.settings
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, path: str, value):
        """Définit une valeur de paramètre par son chemin."""
        try:
            keys = path.split('.')
            current = self.settings
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = value
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la définition de {path}: {e}")
            return False
    
    def get_resolution(self) -> Tuple[int, int]:
        """Retourne la résolution actuelle."""
        res = self.get("video.resolution", [800, 600])
        return tuple(res)
    
    def set_resolution(self, width: int, height: int):
        """Définit la résolution."""
        self.set("video.resolution", [width, height])
        self.save_settings()
    
    def get_master_volume(self) -> float:
        """Retourne le volume principal (0.0 à 1.0)."""
        return self.get("audio.master_volume", 0.7)
    
    def get_music_volume(self) -> float:
        """Retourne le volume de la musique (0.0 à 1.0)."""
        return self.get("audio.music_volume", 0.5)
    
    def get_sfx_volume(self) -> float:
        """Retourne le volume des effets sonores (0.0 à 1.0)."""
        return self.get("audio.sfx_volume", 0.8)
    
    def set_master_volume(self, volume: float, auto_save: bool = True):
        """Définit le volume principal."""
        volume = max(0.0, min(1.0, volume))
        self.set("audio.master_volume", volume)
        
        # Appliquer immédiatement le volume
        self.apply_audio_settings()
        
        if auto_save:
            self.save_settings()
    
    def set_music_volume(self, volume: float, auto_save: bool = True):
        """Définit le volume de la musique."""
        volume = max(0.0, min(1.0, volume))
        self.set("audio.music_volume", volume)
        
        # Appliquer immédiatement le volume
        self.apply_audio_settings()
        
        if auto_save:
            self.save_settings()
    
    def set_sfx_volume(self, volume: float, auto_save: bool = True):
        """Définit le volume des effets sonores."""
        volume = max(0.0, min(1.0, volume))
        self.set("audio.sfx_volume", volume)
        
        if auto_save:
            self.save_settings()
    
    def get_hud_scale(self) -> float:
        """Retourne l'échelle de l'HUD."""
        return self.get("hud.scale", 1.0)
    
    def set_hud_scale(self, scale: float, auto_save: bool = True):
        """Définit l'échelle de l'HUD."""
        scale = max(0.5, min(2.0, scale))
        self.set("hud.scale", scale)
        if auto_save:
            self.save_settings()
    
    def get_timer_enabled(self) -> bool:
        """Retourne si le timer est activé."""
        return self.get("hud.show_timer", True)
    
    def set_timer_enabled(self, enabled: bool):
        """Active/désactive le timer."""
        self.set("hud.show_timer", enabled)
        self.save_settings()
    
    def get_keybind(self, action: str):
        """Retourne la touche associée à une action."""
        return self.get(f"keybinds.{action}", None)
    
    def set_keybind(self, action: str, key):
        """Définit la touche pour une action."""
        self.set(f"keybinds.{action}", key)
        self.save_settings()
    
    def get_available_resolutions(self) -> List[Tuple[int, int]]:
        """Retourne la liste des résolutions disponibles."""
        return self.available_resolutions
    
    def apply_audio_settings(self):
        """Applique les paramètres audio actuels."""
        try:
            master_vol = self.get_master_volume()
            music_vol = self.get_music_volume()
            sfx_vol = self.get_sfx_volume()
            
            # Appliquer le volume de la musique
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(master_vol * music_vol)
            
            # Mettre à jour les volumes SFX via l'audio manager
            try:
                from .audio_manager import audio_manager
                audio_manager.update_all_volumes()
            except ImportError:
                pass  # L'audio manager n'est pas encore disponible
            
            print(f"🔊 Audio appliqué - Master: {master_vol:.1f}, Musique: {music_vol:.1f}, SFX: {sfx_vol:.1f}")
        except Exception as e:
            print(f"⚠️ Erreur lors de l'application audio: {e}")
    
    def reset_to_defaults(self):
        """Remet tous les paramètres par défaut."""
        self.settings = self.default_settings.copy()
        self.save_settings()
        print("🔄 Paramètres remis par défaut")

# Instance globale
settings = SettingsManager() 