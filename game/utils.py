# game/utils.py
import sys
import os

def resource_path(relative_path):
    """
    Renvoie le chemin absolu vers une ressource, en développement
    ou dans un .exe PyInstaller.
    - sous PyInstaller :   sys._MEIPASS pointe sur le dossier temporaire
    - sinon : le dossier parent de game/ (racine du projet)
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # on remonte d’un cran depuis game/ vers la racine du projet
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    return os.path.join(base_path, relative_path)
