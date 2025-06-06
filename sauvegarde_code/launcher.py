#!/usr/bin/env python3
"""
Launcher pour Death Must Pygame
Point d'entrée qui corrige les problèmes d'imports relatifs avec PyInstaller
"""

import sys
import os

# Fonction pour obtenir le chemin des ressources
def resource_path(relative_path):
    """Obtient le chemin absolu vers une ressource, fonctionne pour dev et PyInstaller"""
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Configurer le working directory pour PyInstaller
if getattr(sys, 'frozen', False):
    # Si c'est un exécutable PyInstaller
    application_path = sys._MEIPASS
    # Changer le working directory vers le dossier de l'exe
    os.chdir(os.path.dirname(sys.executable))
else:
    # Si c'est un script Python normal
    application_path = os.path.dirname(os.path.abspath(__file__))

# Ajouter le dossier game au path Python
game_path = os.path.join(application_path, 'game')
if game_path not in sys.path:
    sys.path.insert(0, game_path)

# S'assurer que les dossiers d'assets existent ou les créer en copiant depuis _MEIPASS
if getattr(sys, 'frozen', False):
    import shutil
    current_dir = os.path.dirname(sys.executable)
    
    # Dossiers à copier/vérifier
    required_dirs = ['assets', 'fx', 'config']
    
    for dir_name in required_dirs:
        src_dir = resource_path(dir_name)
        dest_dir = os.path.join(current_dir, dir_name)
        
        if os.path.exists(src_dir) and not os.path.exists(dest_dir):
            print(f"📁 Copie des {dir_name}...")
            shutil.copytree(src_dir, dest_dir)
        elif not os.path.exists(dest_dir):
            print(f"⚠️ Dossier manquant: {dir_name}")

# Maintenant importer et lancer le jeu
try:
    from game.main import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Erreur d'import: {e}")
    print("Tentative d'import direct...")
    try:
        import main
        main.main()
    except Exception as e2:
        print(f"Erreur lors du lancement: {e2}")
        print("Vérifiez que tous les fichiers sont présents...")
        input("Appuyez sur Entrée pour fermer...") 