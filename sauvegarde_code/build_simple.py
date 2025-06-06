#!/usr/bin/env python3
"""
Script de build simplifié pour Death Must Pygame
Évite les problèmes de dépendances complexes
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build():
    """Nettoie les builds précédents"""
    for folder in ["build", "dist", "__pycache__"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🧹 Nettoyé: {folder}")
    
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"🧹 Supprimé: {spec_file}")

def build_simple():
    """Build simplifié avec PyInstaller"""
    
    print("🎮 Build simplifié de Death Must Pygame")
    print("=" * 50)
    
    # Nettoyage
    clean_build()
    
    # Commande PyInstaller simplifiée avec le nouveau launcher
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onedir",                    # Mode dossier (plus fiable)
        "--console",                   # Avec console pour débugger
        "--clean",                     # Nettoyage
        "--noconfirm",                 # Pas de confirmation
        "--name", "DeathMustPygame",   # Nom de l'exe
        "--add-data", "game;game",     # Dossier game entier
        "--add-data", "assets;assets", # Assets
        "--add-data", "fx;fx",         # Sons
        "--add-data", "config;config", # Config
        "--collect-all", "pygame",     # Tout pygame
        "--hidden-import", "pygame",
        "--hidden-import", "pygame.mixer",
        "--hidden-import", "pygame.font",
        "--hidden-import", "pygame.freetype",
        "--hidden-import", "json",
        "--hidden-import", "pathlib",
        "--hidden-import", "random",
        "--hidden-import", "game.main",
        "--hidden-import", "game.settings",
        "--hidden-import", "game.player",
        "--hidden-import", "game.enemy",
        "--hidden-import", "game.xp_orb",
        "--hidden-import", "game.goblin_mage",
        "--hidden-import", "game.boss",
        "--hidden-import", "game.balance_menu",
        "--hidden-import", "game.pause_system",
        "--hidden-import", "game.balance_manager",
        "--hidden-import", "game.settings_menu",
        "--hidden-import", "game.settings_manager",
        "--hidden-import", "game.audio_manager",
        "--exclude-module", "tkinter",
        "--exclude-module", "unittest",
        "--exclude-module", "test",
        "--exclude-module", "jaraco",          # Exclure jaraco pour éviter les problèmes
        "--exclude-module", "pkg_resources",   # Exclure pkg_resources problématique
        "--exclude-module", "setuptools",
        "--exclude-module", "pip",
        "launcher.py"                          # Utiliser le launcher au lieu de game/main.py
    ]
    
    print("🔨 Construction en cours...")
    print(f"📋 Commande: {' '.join(cmd[:15])}...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build réussi!")
        
        # Vérification du résultat
        exe_path = Path("dist/DeathMustPygame/DeathMustPygame.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📦 Exécutable créé: {exe_path} ({size_mb:.1f} MB)")
            
            # Test rapide de l'exe
            print("\n🧪 Test rapide de l'exécutable...")
            test_result = subprocess.run([str(exe_path), "--help"], 
                                       capture_output=True, text=True, timeout=10)
            if test_result.returncode == 0:
                print("✅ L'exécutable semble fonctionner")
            else:
                print(f"⚠️ Test non concluant (code: {test_result.returncode})")
            
            return True
        else:
            print("❌ Exécutable non trouvé après le build")
            return False
            
    except subprocess.CalledProcessError as e:
        print("❌ Erreur lors du build:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except subprocess.TimeoutExpired:
        print("⚠️ Test de l'exécutable interrompu (timeout)")
        return True  # Le build a réussi même si le test a échoué

def create_launcher():
    """Crée un script de lancement alternatif"""
    launcher_content = """@echo off
echo Lancement de Death Must Pygame...
cd /d "%~dp0"
DeathMustPygame.exe
if errorlevel 1 (
    echo.
    echo Erreur lors du lancement du jeu.
    echo Appuyez sur une touche pour voir les details...
    pause
    DeathMustPygame.exe
)
"""
    
    with open("dist/DeathMustPygame/Lancer_Jeu.bat", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    print("✅ Script de lancement créé: Lancer_Jeu.bat")

if __name__ == "__main__":
    if build_simple():
        create_launcher()
        print("\n🎉 Build terminé avec succès!")
        print("📁 Fichiers dans: dist/DeathMustPygame/")
        print("🚀 Utilisez Lancer_Jeu.bat pour tester")
    else:
        print("\n❌ Échec du build")
        sys.exit(1) 