@echo off
echo ========================================================
echo       Death Must Pygame - Launcher Direct
echo ========================================================
echo.
echo 🎮 Lancement direct du jeu (evite les problemes d'antivirus)
echo.

REM Vérifier que Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installe ou pas dans le PATH
    echo.
    echo 📋 Installez Python depuis python.org puis relancez ce script
    pause
    exit /b 1
)

echo ✅ Python detecte

REM Vérifier les dépendances
echo 📋 Verification des dependances...
python -c "import pygame; import numpy; import PIL" 2>nul
if errorlevel 1 (
    echo ⚠️ Installation des dependances manquantes...
    pip install pygame numpy pillow
    if errorlevel 1 (
        echo ❌ Erreur lors de l'installation des dependances
        pause
        exit /b 1
    )
)

echo ✅ Dependances OK

echo.
echo 🚀 Lancement du jeu...
python launcher.py

if errorlevel 1 (
    echo.
    echo ❌ Erreur lors du lancement
    pause
)

echo.
echo 🎯 Jeu ferme
pause 