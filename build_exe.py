#!/usr/bin/env python3
"""
Script de build automatisé pour créer un .exe de Death Must Pygame
Utilise PyInstaller pour générer un exécutable Windows distributable

Usage:
    python build_exe.py [--onefile] [--windowed] [--clean]
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path

def check_requirements():
    """Vérifie que tous les pré-requis sont installés"""
    try:
        import PyInstaller
        print("✅ PyInstaller trouvé")
    except ImportError:
        print("❌ PyInstaller non trouvé. Installation...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installé")
    
    try:
        import pygame
        print("✅ pygame trouvé")
    except ImportError:
        print("❌ pygame requis pour le build")
        sys.exit(1)

def clean_build():
    """Nettoie les dossiers de build précédents"""
    folders_to_clean = ["build", "dist", "__pycache__"]
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🧹 Nettoyé: {folder}")
    
    # Nettoie les fichiers .spec existants
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"🧹 Supprimé: {spec_file}")

def create_version_file():
    """Crée un fichier de version pour l'exe Windows"""
    version_content = """
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Death Must Pygame'),
        StringStruct(u'FileDescription', u'Reincarnation of the unkillable last human against all gods'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'DeathMustPygame'),
        StringStruct(u'LegalCopyright', u''),
        StringStruct(u'OriginalFilename', u'DeathMustPygame.exe'),
        StringStruct(u'ProductName', u'Death Must Pygame'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    with open("version.txt", "w", encoding="utf-8") as f:
        f.write(version_content)
    print("✅ Fichier de version créé")

def get_pygame_data_paths():
    """Récupère les chemins des données pygame nécessaires"""
    import pygame
    pygame_path = Path(pygame.__file__).parent
    
    data_files = []
    
    # Ajouter les DLLs pygame si elles existent
    pygame_dlls = pygame_path / "pygame"
    if pygame_dlls.exists():
        for dll in pygame_dlls.glob("*.dll"):
            data_files.append((str(dll), "."))
    
    return data_files

def get_hidden_imports():
    """Récupère automatiquement les modules cachés nécessaires"""
    hidden_imports = [
        # Core pygame
        "pygame",
        "pygame.mixer",
        "pygame.font", 
        "pygame.freetype",
        "pygame.gfxdraw",
        "pygame.image",
        "pygame.transform",
        "pygame.surfarray",
        "pygame.math",
        "pygame.time",
        "pygame.event",
        "pygame.key",
        "pygame.mouse",
        "pygame.display",
        "pygame.surface",
        "pygame.rect",
        "pygame.sprite",
        "pygame.mask",
        
        # Dépendances scientifiques
        "numpy",
        "numpy.core",
        "numpy.core._multiarray_umath",
        "numpy.core._multiarray_tests",
        "numpy.fft._pocketfft_umath",
        "numpy.linalg._umath_linalg",
        "numpy.random.bit_generator",
        "numpy.random.mtrand",
        "numpy.random._bounded_integers",
        "numpy.random._common",
        "numpy.random._generator",
        "numpy.random._mt19937",
        "numpy.random._pcg64",
        "numpy.random._philox",
        "numpy.random._sfc64",
        
        # PIL/Pillow
        "PIL",
        "PIL.Image",
        "PIL.ImageFilter",
        "PIL.ImageEnhance",
        "PIL._imaging",
        "PIL._imagingcms",
        "PIL._imagingmath",
        "PIL._webp",
        
        # Modules système
        "json",
        "pathlib",
        "random",
        "math",
        "os",
        "sys",
        "time",
        "collections",
        
        # Dépendances cachées problématiques
        "jaraco",
        "jaraco.text",
        "pkg_resources",
        "pkg_resources.py31compat",
        "importlib_metadata",
        "importlib_metadata._adapters",
        "importlib_metadata._meta",
        "zipp",
        "packaging",
        "packaging.version",
        "packaging.specifiers",
        "packaging.requirements",
        
        # Autres dépendances communes
        "six",
        "setuptools",
        "distutils",
        "email",
        "email.mime",
        "email.mime.text",
        "urllib",
        "urllib.parse",
        "urllib.request",
        "ssl",
        "socket",
        "select",
        "threading",
        "queue",
        "multiprocessing",
        "concurrent.futures",
        "logging",
        "weakref",
        "gc",
        "platform",
        "traceback",
        "warnings",
        "contextlib",
        "functools",
        "itertools",
        "operator",
        "types",
        "copy",
        "pickle",
        "base64",
        "hashlib",
        "hmac",
        "binascii",
        "struct",
        "array",
        "io",
        "codecs",
        "locale",
        "datetime",
        "calendar",
        "re",
        "string",
        "textwrap",
        "unicodedata",
        "encodings",
        "encodings.utf_8",
        "encodings.cp1252",
        "encodings.latin_1"
    ]
    
    # Vérifier quels modules sont disponibles
    available_imports = []
    for module in hidden_imports:
        try:
            __import__(module)
            available_imports.append(module)
            print(f"✅ Module trouvé: {module}")
        except ImportError:
            print(f"⚠️ Module non trouvé: {module}")
    
    return available_imports

def build_executable(onefile=False, windowed=False):
    """Construit l'exécutable avec PyInstaller"""
    
    # Arguments de base pour PyInstaller
    args = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "--name", "DeathMustPygame",
        "--version-file", "version.txt",
    ]
    
    # Ajouter l'icône seulement si elle existe
    icon_path = "assets/icon.ico"
    if os.path.exists(icon_path):
        args.extend(["--icon", icon_path])
        print(f"✅ Icône trouvée: {icon_path}")
    else:
        print(f"⚠️ Pas d'icône trouvée ({icon_path}), création sans icône")
    
    # Mode de build
    if onefile:
        args.append("--onefile")
    else:
        args.append("--onedir")
    
    # Mode fenêtré (sans console)
    if windowed:
        args.append("--windowed")
    else:
        args.append("--console")
    
    # Ajout des assets et fichiers de données
    data_dirs = [
        "assets",
        "fx", 
        "config"
    ]
    
    for data_dir in data_dirs:
        if os.path.exists(data_dir):
            args.extend(["--add-data", f"{data_dir};{data_dir}"])
            print(f"✅ Dossier ajouté: {data_dir}")
    
    # Modules cachés avec détection automatique
    print("\n🔍 Détection des modules cachés...")
    hidden_imports = get_hidden_imports()
    
    for module in hidden_imports:
        args.extend(["--hidden-import", module])
    
    # Exclusions pour réduire la taille
    excludes = [
        "tkinter",
        "unittest",
        "test",
        "distutils.tests",
        "setuptools.tests",
        "pip._internal.tests",
        "pydoc",
        "pdb",
        "doctest",
        "turtle",
        "turtledemo",
        "lib2to3",
        "ctypes.test",
        "sqlite3.test",
        "test.test_asyncio",
        "test.test_subprocess",
    ]
    
    for exclude in excludes:
        args.extend(["--exclude-module", exclude])
    
    # Options supplémentaires pour résoudre les problèmes
    args.extend([
        "--collect-all", "pygame",
        "--collect-all", "pkg_resources",
        "--copy-metadata", "pygame",
        "--copy-metadata", "setuptools",
        "--recursive-copy-metadata", "pygame",
    ])
    
    # Script principal
    args.append("game/main.py")
    
    print(f"\n🔨 Construction de l'exécutable avec {len(hidden_imports)} modules cachés...")
    print(f"📋 Commande: {' '.join(args[:10])}... ({len(args)} arguments total)")
    
    # Exécution de PyInstaller
    result = subprocess.run(args, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build réussi!")
        
        # Informations sur le résultat
        if onefile:
            exe_path = Path("dist") / "DeathMustPygame.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Exécutable créé: {exe_path} ({size_mb:.1f} MB)")
        else:
            dist_folder = Path("dist") / "DeathMustPygame"
            if dist_folder.exists():
                total_size = sum(f.stat().st_size for f in dist_folder.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)
                print(f"📦 Dossier créé: {dist_folder} ({size_mb:.1f} MB)")
                
        return True
    else:
        print("❌ Erreur lors du build:")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False

def create_readme():
    """Crée un README pour la distribution"""
    readme_content = """# Death Must Pygame - Distribution

## Comment jouer

### Exécutable unique (.exe)
Double-cliquez sur `DeathMustPygame.exe` pour lancer le jeu.

### Dossier de distribution
1. Naviguez dans le dossier `DeathMustPygame`
2. Double-cliquez sur `DeathMustPygame.exe`

## Contrôles
- ZQSD : Se déplacer
- ESPACE : Dash
- Clic gauche : Attaquer
- Clic droit : Cri
- F1 : Menu d'équilibrage (pendant le jeu)
- ESC : Pause

## Configuration
Le jeu sauvegarde automatiquement vos paramètres dans le dossier `config/`.

## Dépannage
Si le jeu ne se lance pas :
1. Vérifiez que votre antivirus ne bloque pas l'exécutable
2. Essayez de lancer en tant qu'administrateur
3. Vérifiez que Visual C++ Redistributable est installé

## Système requis
- Windows 10/11 (64-bit)
- DirectX 11 compatible
- 100 MB d'espace disque libre
"""
    
    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ README créé")

def main():
    parser = argparse.ArgumentParser(description="Build Death Must Pygame executable")
    parser.add_argument("--onefile", action="store_true", 
                       help="Créer un seul fichier .exe (plus lent au démarrage)")
    parser.add_argument("--windowed", action="store_true",
                       help="Créer un .exe sans console (mode fenêtré)")
    parser.add_argument("--clean", action="store_true",
                       help="Nettoyer les builds précédents avant de commencer")
    
    args = parser.parse_args()
    
    print("🎮 Build de Death Must Pygame")
    print("=" * 50)
    
    # Vérification des pré-requis
    check_requirements()
    
    # Nettoyage si demandé
    if args.clean:
        clean_build()
    
    # Création du fichier de version
    create_version_file()
    
    # Build de l'exécutable
    success = build_executable(onefile=args.onefile, windowed=args.windowed)
    
    if success:
        # Création du README
        create_readme()
        
        print("\n🎉 Build terminé avec succès!")
        print(f"📁 Fichiers disponibles dans le dossier 'dist/'")
        
        if args.onefile:
            print("\n💡 Mode onefile: L'exécutable est autonome mais plus lent au démarrage")
        else:
            print("\n💡 Mode onedir: Démarrage plus rapide, distribuez tout le dossier")
            
        print("\n📋 Conseils pour la distribution:")
        print("  - Testez l'exe sur une machine différente")
        print("  - Créez un zip pour faciliter la distribution")
        print("  - Ajoutez un antivirus scan pour rassurer les utilisateurs")
        
    else:
        print("\n❌ Échec du build")
        sys.exit(1)

if __name__ == "__main__":
    main() 