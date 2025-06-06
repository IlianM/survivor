"""
Gestionnaire audio pour Death Must Pygame.
Applique les volumes configurés aux sons du jeu.
"""

import pygame
from .settings_manager import settings

class AudioManager:
    """Gestionnaire centralisé pour l'audio du jeu."""
    
    def __init__(self):
        self.sounds = {}
        
    def load_sound(self, name: str, path: str):
        """Charge un son et le stocke."""
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            return sound
        except pygame.error as e:
            print(f"⚠️ Erreur lors du chargement du son {name}: {e}")
            return None
    
    def play_sound(self, name: str, volume_override: float = None):
        """Joue un son avec le volume SFX configuré."""
        if name in self.sounds:
            sound = self.sounds[name]
            
            # Calculer le volume final
            master_vol = settings.get_master_volume()
            sfx_vol = settings.get_sfx_volume()
            final_volume = master_vol * sfx_vol
            
            if volume_override is not None:
                final_volume *= volume_override
            
            # Appliquer le volume et jouer
            sound.set_volume(final_volume)
            sound.play()
            return True
        else:
            print(f"⚠️ Son '{name}' non trouvé")
            return False
    
    def get_sound(self, name: str):
        """Retourne un objet Sound pour usage manuel."""
        return self.sounds.get(name, None)
    
    def set_sound_volume(self, name: str, volume: float):
        """Définit le volume d'un son spécifique."""
        if name in self.sounds:
            master_vol = settings.get_master_volume()
            sfx_vol = settings.get_sfx_volume()
            final_volume = master_vol * sfx_vol * volume
            self.sounds[name].set_volume(final_volume)
    
    def update_all_volumes(self):
        """Met à jour le volume de tous les sons chargés."""
        master_vol = settings.get_master_volume()
        sfx_vol = settings.get_sfx_volume()
        final_volume = master_vol * sfx_vol
        
        for sound in self.sounds.values():
            sound.set_volume(final_volume)

# Instance globale
audio_manager = AudioManager() 