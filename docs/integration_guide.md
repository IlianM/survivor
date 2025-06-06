# 🎮 Guide d'Intégration - Menu d'Équilibrage In-Game

## 📋 **Aperçu**

Ce système vous permet d'ajouter un **menu d'équilibrage en temps réel** à votre jeu pygame en seulement quelques lignes de code !

**Fonctionnalités :**
- ⏸️ **Pause automatique** quand le menu s'ouvre
- 🎛️ **Sliders intuitifs** pour modifier les valeurs
- 💾 **Sauvegarde automatique** en JSON
- 📊 **4 onglets** : Joueur, Ennemis, Difficulté, Spawn
- 🔄 **Application instantanée** des changements
- 👥 **Interface simple** pour non-développeurs

---

## 🚀 **Intégration Rapide (3 étapes)**

### **1. Imports**
```python
from game.balance_menu import BalanceMenu
from game.pause_system import pause_system
from game.balance_manager import balance
```

### **2. Initialisation**
```python
class MonJeu:
    def __init__(self):
        # ... votre code existant ...
        
        # Ajouter le menu d'équilibrage
        self.balance_menu = BalanceMenu(screen_width, screen_height)
```

### **3. Intégration dans la boucle principale**
```python
def handle_events(self):
    for event in pygame.event.get():
        # ... vos événements existants ...
        
        # Touche F1 pour ouvrir le menu
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.balance_menu.toggle()
            if self.balance_menu.active:
                pause_system.pause()
            else:
                pause_system.resume()
        
        # Laisser le menu gérer ses événements
        if self.balance_menu.handle_event(event):
            continue

def update(self):
    # Appliquer la pause
    adjusted_dt = pause_system.update(self.dt)
    
    if adjusted_dt > 0:  # Seulement si pas en pause
        # ... votre logique de jeu ...
        
        # Utiliser les stats d'équilibrage
        player_speed = balance.get_player_stats().get("speed", 150)
    
    # Mettre à jour le menu
    self.balance_menu.update(adjusted_dt)

def draw(self):
    # ... votre code de dessin existant ...
    
    # Overlay de pause
    pause_system.draw_pause_overlay(self.screen)
    
    # Menu d'équilibrage (EN DERNIER)
    self.balance_menu.draw(self.screen)
```

---

## 🎛️ **Utilisation des Stats d'Équilibrage**

### **Stats du Joueur**
```python
# Récupérer toutes les stats
player_stats = balance.get_player_stats()

# Stats spécifiques
speed = balance.get_player_stats().get("speed", 150)
damage = balance.get_player_stats().get("attack_damage", 3)
hp = balance.get_player_stats().get("max_hp", 10)
```

### **Stats des Ennemis**
```python
# Par type d'ennemi
normal_hp = balance.get_enemy_stats("normal").get("hp", 15)
boss_damage = balance.get_enemy_stats("boss").get("damage", 8)

# Fonction utilitaire
enemy_speed = get_enemy_stat("goblin_mage", "speed", 60)
```

### **Modification Manuelle**
```python
# Changer une valeur
balance.set_value("player.attack_damage", 5.0)
balance.set_value("enemies.normal.hp", 25)

# Changer la difficulté
balance.set_difficulty("hard")

# Sauvegarder
balance.save_config()
```

---

## ⌨️ **Contrôles**

| Touche | Action |
|--------|--------|
| **F1** | Ouvrir/fermer le menu d'équilibrage |
| **ESPACE** | Pause/reprendre le jeu |
| **ÉCHAP** | Fermer le menu d'équilibrage |
| **Molette** | Défiler dans le menu |
| **Clic & Glisser** | Modifier les sliders |

---

## 📁 **Structure des Fichiers**

```
votre_projet/
├── config/
│   └── balance.json          # Configuration d'équilibrage
├── game/
│   ├── balance_manager.py    # Gestionnaire principal
│   ├── balance_menu.py       # Interface in-game
│   └── pause_system.py       # Système de pause
└── tools/
    └── balance_editor.py     # Éditeur en ligne de commande
```

---

## 🔧 **Personnalisation**

### **Ajouter des Variables**
Dans `balance_menu.py`, section `self.variables` :

```python
"player": {
    "ma_nouvelle_stat": {
        "name": "Ma Stat", 
        "min": 0, 
        "max": 100, 
        "step": 1, 
        "type": int
    }
}
```

### **Modifier les Couleurs**
```python
# Dans BalanceMenu.__init__()
self.accent_color = (255, 100, 100)  # Rouge
self.panel_color = (30, 30, 30)      # Noir
```

### **Ajouter des Onglets**
```python
# Nouvel onglet
self.tabs["powerups"] = "⚡ Power-ups"

# Nouvelles variables
self.variables["powerups"] = {
    "duration": {"name": "Durée", "min": 1, "max": 30, "step": 1, "type": int}
}
```

---

## 📊 **Configuration JSON**

Le fichier `config/balance.json` est automatiquement créé et sauvegardé :

```json
{
    "player": {
        "speed": 150,
        "attack_damage": 3,
        "max_hp": 10
    },
    "enemies": {
        "normal": {"hp": 15, "speed": 80, "damage": 2}
    },
    "difficulty": {
        "normal": {"damage_multiplier": 1.0, "hp_multiplier": 1.0}
    }
}
```

---

## 🎯 **Exemple Complet**

Voir `game/integration_example.py` pour un exemple fonctionnel complet !

**Lancer l'exemple :**
```bash
python game/integration_example.py
```

---

## 🔧 **Dépendances**

- **pygame** : Interface graphique
- **json** : Sauvegarde de configuration (standard Python)
- **typing** : Annotations de type (standard Python)

---

## 💡 **Conseils**

1. **Testez en temps réel** : Modifiez les valeurs pendant que vous jouez
2. **Sauvegarde automatique** : Pas besoin de sauvegarder manuellement
3. **Interface simple** : Parfait pour les non-programmeurs de l'équipe
4. **Versioning** : Le JSON peut être versionné avec git
5. **A/B Testing** : Changez rapidement entre configurations

---

## 🆘 **Support**

- Ouvrez le menu avec **F1**
- Utilisez les **sliders** pour modifier les valeurs
- Les changements sont **instantanés**
- La **sauvegarde** est automatique

**C'est tout ! Votre jeu a maintenant un système d'équilibrage professionnel ! 🎉** 