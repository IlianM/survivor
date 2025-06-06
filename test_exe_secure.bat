@echo off
echo ========================================================
echo   Test Securise de Death Must Pygame
echo ========================================================
echo.

echo 🛡️ IMPORTANT: Ce script va temporairement desactiver l'antivirus
echo    pour tester le jeu. L'antivirus sera reactive automatiquement.
echo.
set /p CHOICE="Continuer? (O/N): "
if /i not "%CHOICE%"=="O" (
    echo Annule.
    pause
    exit /b 0
)

echo.
echo 📋 Etape 1: Verification de l'exe...
if not exist "dist\DeathMustPygame\DeathMustPygame.exe" (
    echo ❌ Executable non trouve!
    echo    Executez d'abord: python build_simple.py
    pause
    exit /b 1
)

echo ✅ Executable trouve

echo.
echo 📋 Etape 2: Sauvegarde des parametres antivirus actuels...
powershell -Command "Get-MpPreference | Select-Object DisableRealtimeMonitoring | Out-File antivirus_backup.txt"

echo.
echo 📋 Etape 3: Desactivation temporaire de l'antivirus...
powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true" 2>nul
if errorlevel 1 (
    echo ⚠️ Impossible de desactiver l'antivirus automatiquement
    echo   Desactivez-le manuellement et appuyez sur une touche...
    pause
) else (
    echo ✅ Antivirus temporairement desactive
)

echo.
echo 📋 Etape 4: Test de l'executable...
echo 🎮 Lancement du jeu...
echo.

cd "dist\DeathMustPygame"
DeathMustPygame.exe

echo.
echo 📋 Etape 5: Reactivation de l'antivirus...
powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $false" 2>nul
if errorlevel 1 (
    echo ⚠️ Reactivez manuellement votre antivirus!
) else (
    echo ✅ Antivirus reactive
)

cd ..\..

echo.
echo 🎯 Test termine!
echo.
echo Si le jeu a fonctionne, vous pouvez:
echo 1. Ajouter une exception permanente pour le dossier dist\
echo 2. Ou utiliser ce script pour jouer
echo.
pause 