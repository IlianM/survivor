# 🎮 Guide de Génération d'Exécutable - Death Must Pygame

Ce guide vous explique comment créer facilement un fichier `.exe` distributable de votre jeu Death Must Pygame.

## 📋 Prérequis

### Obligatoires
- ✅ **Python 3.8+** installé
- ✅ **pygame** installé (`pip install pygame`)
- ✅ **PyInstaller** (sera installé automatiquement)

### Optionnels
- 🎨 **Icône du jeu** : `assets/icon.ico` (format ICO pour Windows)
- 📦 **UPX** pour compresser l'exécutable (optionnel)

## 🚀 Méthodes de Build

### Méthode 1 : Script Automatisé (Recommandé)

#### Windows
```bash
# Double-cliquez sur build_exe.bat
# OU en ligne de commande :
build_exe.bat
```

#### Toutes plateformes
```bash
# Build standard (dossier de distribution)
python build_exe.py

# Build en un seul fichier exe
python build_exe.py --onefile

# Build sans console (mode fenêtré)
python build_exe.py --windowed

# Nettoyer avant de construire
python build_exe.py --clean

# Combinaisons possibles
python build_exe.py --onefile --windowed --clean
```

### Méthode 2 : Configuration Avancée

```bash
# Utiliser le fichier .spec prédéfini
pyinstaller build_config.spec
```

### Méthode 3 : PyInstaller Direct (Basique)

```bash
# Installation si nécessaire
pip install pyinstaller

# Build basique
pyinstaller --onefile --name "DeathMustPygame" game/main.py

# Build avec assets
pyinstaller --onefile --add-data "assets;assets" --add-data "fx;fx" --add-data "config;config" --name "DeathMustPygame" game/main.py
```

## 🎯 Types de Build

### 📁 OneDIR (Recommandé)
- **Avantages** : Démarrage rapide, plus facile à déboguer
- **Inconvénients** : Plusieurs fichiers à distribuer
- **Usage** : `python build_exe.py`
- **Résultat** : Dossier `dist/DeathMustPygame/` avec exe + DLLs

### 📦 OneFile
- **Avantages** : Un seul fichier .exe à distribuer
- **Inconvénients** : Démarrage plus lent (extraction temporaire)
- **Usage** : `python build_exe.py --onefile`
- **Résultat** : Fichier unique `dist/DeathMustPygame.exe`

### 🖼️ Windowed vs Console
- **Console** : Affiche une fenêtre de console (utile pour débuggage)
- **Windowed** : Pas de console (plus propre pour distribution)
- **Usage** : Ajoutez `--windowed` à la commande

## 📂 Structure de Sortie

```
dist/
├── DeathMustPygame/           # Mode OneDIR
│   ├── DeathMustPygame.exe    # Exécutable principal
│   ├── assets/                # Assets du jeu
│   ├── fx/                    # Sons et musiques
│   ├── config/                # Configuration
│   └── [DLLs et bibliothèques]
├── DeathMustPygame.exe        # Mode OneFile
└── README.txt                 # Instructions pour l'utilisateur
```

## 🛠️ Configuration Avancée

### Personnaliser l'icône
Placez votre icône au format `.ico` dans `assets/icon.ico`

### Modifier les informations de version
Éditez le fichier `version.txt` généré automatiquement ou modifiez la fonction `create_version_file()` dans `build_exe.py`

### Exclure des modules
Modifiez la liste `excludes` dans `build_exe.py` pour réduire la taille :
```python
excludes = [
    "tkinter",
    "unittest", 
    "test",
    # Ajoutez d'autres modules à exclure
]
```

### Inclure des modules additionnels
Modifiez la liste `hidden_imports` dans `build_exe.py` :
```python
hidden_imports = [
    "pygame",
    "numpy",
    # Ajoutez d'autres modules requis
]
```

## ⚠️ Résolution de Problèmes

### Problème : L'exe ne se lance pas
**Solutions :**
1. Vérifiez que tous les assets sont dans le bon dossier
2. Testez d'abord en mode console pour voir les erreurs
3. Vérifiez que Visual C++ Redistributable est installé sur la machine cible

### Problème : Fichier trop volumineux
**Solutions :**
1. Ajoutez plus de modules à `excludes`
2. Utilisez UPX pour compresser : `pip install upx-python`
3. Utilisez le mode OneDIR au lieu de OneFile

### Problème : Antivirus signale une menace
**Solutions :**
1. C'est normal pour les exécutables créés par PyInstaller
2. Ajoutez une exception dans votre antivirus
3. Uploadez sur VirusTotal pour vérifier
4. Signez votre exécutable avec un certificat de code

### Problème : Sons/images ne se chargent pas
**Solutions :**
1. Vérifiez que les dossiers `assets/` et `fx/` sont inclus
2. Modifiez les chemins dans le code pour utiliser des chemins relatifs
3. Utilisez `sys._MEIPASS` pour les chemins dans un exécutable PyInstaller

## 📦 Distribution

### Format ZIP
```bash
# Créer une archive pour distribution
# Mode OneDIR
zip -r DeathMustPygame-v1.0.zip dist/DeathMustPygame/

# Mode OneFile
zip DeathMustPygame-v1.0.zip dist/DeathMustPygame.exe dist/README.txt
```

### Checklist avant distribution
- [ ] Testez l'exe sur une machine différente
- [ ] Vérifiez que tous les assets se chargent correctement
- [ ] Testez avec un antivirus actif
- [ ] Incluez un README avec instructions d'installation
- [ ] Mentionnez les prérequis système

## 🔧 Scripts Utiles

### Commandes rapides
```bash
# Build de développement avec console
python build_exe.py --clean

# Build de production sans console
python build_exe.py --onefile --windowed --clean

# Test rapide
python build_exe.py --clean && dist/DeathMustPygame/DeathMustPygame.exe
```

### Automatisation CI/CD
Le script `build_exe.py` peut être intégré dans des workflows GitHub Actions ou autres pipelines CI/CD.

## 💡 Conseils

1. **Testez toujours** sur une machine propre sans Python installé
2. **Utilisez OneDIR** pour le développement et OneFile pour la distribution finale
3. **Gardez un mode console** pendant le développement pour le débogage
4. **Documentez les prérequis** système pour vos utilisateurs
5. **Considérez la signature de code** pour éviter les alertes de sécurité

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs de PyInstaller
2. Testez d'abord une version console
3. Consultez la documentation PyInstaller officielle
4. Cherchez des solutions spécifiques à pygame sur les forums

---

**Bon build ! 🎮** 