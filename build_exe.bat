@echo off
REM Script batch pour créer un .exe de Death Must Pygame
REM Usage: build_exe.bat [onefile] [windowed] [clean]

echo.
echo ============================================================
echo      Death Must Pygame - Generateur d'executable
echo ============================================================
echo.

REM Vérification de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo    Installez Python depuis python.org
    pause
    exit /b 1
)

echo ✅ Python détecté

REM Création des arguments
set ARGS=
if "%1"=="onefile" set ARGS=%ARGS% --onefile
if "%2"=="onefile" set ARGS=%ARGS% --onefile
if "%3"=="onefile" set ARGS=%ARGS% --onefile

if "%1"=="windowed" set ARGS=%ARGS% --windowed
if "%2"=="windowed" set ARGS=%ARGS% --windowed
if "%3"=="windowed" set ARGS=%ARGS% --windowed

if "%1"=="clean" set ARGS=%ARGS% --clean
if "%2"=="clean" set ARGS=%ARGS% --clean
if "%3"=="clean" set ARGS=%ARGS% --clean

echo.
echo 🚀 Lancement du build avec les options: %ARGS%
echo.

REM Exécution du script Python de build
python build_exe.py %ARGS%

if errorlevel 1 (
    echo.
    echo ❌ Erreur lors du build
    pause
    exit /b 1
)

echo.
echo ✅ Build terminé avec succès!
echo.
echo 📁 Fichiers générés dans le dossier 'dist/'
echo.

REM Proposition d'ouvrir le dossier de destination
set /p CHOICE="Voulez-vous ouvrir le dossier dist? (O/N): "
if /i "%CHOICE%"=="O" (
    explorer dist
)

pause 