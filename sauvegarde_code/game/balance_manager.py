"""
Gestionnaire de configuration pour l'équilibrage du jeu.
Permet de charger, modifier et sauvegarder les paramètres facilement.
"""

import json
import os
from typing import Dict, Any, Optional

class BalanceManager:
    """Gestionnaire centralisé de tous les paramètres d'équilibrage."""
    
    def __init__(self, config_path: str = "config/balance.json"):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.difficulty_level = "normal"
        self.load_config()
    
    def load_config(self) -> bool:
        """Charge la configuration depuis le fichier JSON."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Configuration chargée: {self.config_path}")
                return True
            else:
                print(f"⚠️ Fichier de config non trouvé: {self.config_path}")
                self._create_default_config()
                return False
        except Exception as e:
            print(f"❌ Erreur chargement config: {e}")
            self._create_default_config()
            return False
    
    def save_config(self) -> bool:
        """Sauvegarde la configuration actuelle."""
        try:
            # Créer le dossier si nécessaire
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Mettre à jour les métadonnées
            import datetime
            self.config["meta"]["last_modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuration sauvegardée: {self.config_path}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde config: {e}")
            return False
    
    def get_player_stats(self) -> Dict[str, Any]:
        """Retourne les stats du joueur avec multiplicateurs de difficulté."""
        base_stats = self.config.get("player", {}).copy()
        difficulty = self.get_difficulty_multipliers()
        
        # Appliquer les multiplicateurs de difficulté
        if "damage_multiplier" in difficulty:
            base_stats["attack_damage"] = base_stats.get("attack_damage", 3) * difficulty["damage_multiplier"]
        
        return base_stats
    
    def get_enemy_stats(self, enemy_type: str) -> Dict[str, Any]:
        """Retourne les stats d'un type d'ennemi avec multiplicateurs."""
        base_stats = self.config.get("enemies", {}).get(enemy_type, {}).copy()
        difficulty = self.get_difficulty_multipliers()
        
        # Appliquer les multiplicateurs de difficulté
        if "hp_multiplier" in difficulty:
            base_stats["hp"] = int(base_stats.get("hp", 15) * difficulty["hp_multiplier"])
        if "damage_multiplier" in difficulty:
            base_stats["damage"] = int(base_stats.get("damage", 2) * difficulty["damage_multiplier"])
        if "xp_multiplier" in difficulty:
            base_stats["xp_value"] = int(base_stats.get("xp_value", 10) * difficulty["xp_multiplier"])
        
        return base_stats
    
    def get_difficulty_multipliers(self) -> Dict[str, float]:
        """Retourne les multiplicateurs de la difficulté actuelle."""
        return self.config.get("difficulty", {}).get(self.difficulty_level, {
            "damage_multiplier": 1.0,
            "hp_multiplier": 1.0,
            "xp_multiplier": 1.0,
            "spawn_rate_multiplier": 1.0
        })
    
    def set_difficulty(self, level: str) -> bool:
        """Change le niveau de difficulté."""
        available_difficulties = list(self.config.get("difficulty", {}).keys())
        if level in available_difficulties:
            self.difficulty_level = level
            print(f"🎯 Difficulté changée: {level}")
            return True
        else:
            print(f"❌ Difficulté inconnue: {level}. Disponibles: {available_difficulties}")
            return False
    
    def get_value(self, path: str, default: Any = None) -> Any:
        """
        Récupère une valeur par son chemin (ex: "player.attack_damage").
        """
        try:
            keys = path.split('.')
            value = self.config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_value(self, path: str, value: Any) -> bool:
        """
        Modifie une valeur par son chemin (ex: "player.attack_damage", 5).
        """
        try:
            keys = path.split('.')
            target = self.config
            
            # Naviguer jusqu'au parent
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
            
            # Modifier la valeur finale
            target[keys[-1]] = value
            print(f"🔧 {path} = {value}")
            return True
        except Exception as e:
            print(f"❌ Erreur modification {path}: {e}")
            return False
    
    def reload_config(self) -> bool:
        """Recharge la configuration depuis le fichier."""
        print("🔄 Rechargement de la configuration...")
        return self.load_config()
    
    def _create_default_config(self):
        """Crée une configuration par défaut si le fichier n'existe pas."""
        self.config = {
            "player": {
                "speed": 150,
                "max_hp": 10,
                "attack_damage": 3,
                "attack_range": 150,
                "attack_cooldown": 1.0
            },
            "enemies": {
                "normal": {"hp": 15, "speed": 80, "damage": 2, "xp_value": 10}
            },
            "difficulty": {
                "normal": {"damage_multiplier": 1.0, "hp_multiplier": 1.0, "xp_multiplier": 1.0}
            },
            "meta": {"version": "1.0.0", "notes": "Configuration par défaut"}
        }
        print("🆕 Configuration par défaut créée")
    
    # Méthodes de convenance pour l'équilibrage rapide
    def quick_balance_player_damage(self, new_damage: float):
        """Modification rapide des dégâts du joueur."""
        self.set_value("player.attack_damage", new_damage)
    
    def quick_balance_enemy_hp(self, enemy_type: str, new_hp: int):
        """Modification rapide des HP d'un ennemi."""
        self.set_value(f"enemies.{enemy_type}.hp", new_hp)
    
    def quick_balance_spawn_rate(self, new_rate: float):
        """Modification rapide du taux de spawn."""
        self.set_value("spawning.base_spawn_rate", new_rate)
    
    def get_balance_summary(self) -> str:
        """Retourne un résumé des paramètres d'équilibrage."""
        player = self.get_player_stats()
        difficulty = self.get_difficulty_multipliers()
        
        summary = f"""
🎮 RÉSUMÉ D'ÉQUILIBRAGE (Difficulté: {self.difficulty_level})
================================================
👤 JOUEUR:
   • Dégâts: {player.get('attack_damage', 'N/A')}
   • HP: {player.get('max_hp', 'N/A')}
   • Vitesse: {player.get('speed', 'N/A')}
   • Portée: {player.get('attack_range', 'N/A')}

🏹 MULTIPLICATEURS:
   • Dégâts: x{difficulty.get('damage_multiplier', 1.0)}
   • HP ennemis: x{difficulty.get('hp_multiplier', 1.0)}
   • XP: x{difficulty.get('xp_multiplier', 1.0)}
   • Spawn: x{difficulty.get('spawn_rate_multiplier', 1.0)}

👹 ENNEMIS:
"""
        for enemy_type in self.config.get("enemies", {}):
            stats = self.get_enemy_stats(enemy_type)
            summary += f"   • {enemy_type}: {stats.get('hp', 'N/A')} HP, {stats.get('damage', 'N/A')} dégâts\n"
        
        return summary

# Instance globale
balance = BalanceManager()

# Fonctions utilitaires pour l'accès rapide
def get_player_stat(stat_name: str, default: Any = None):
    """Accès rapide aux stats du joueur."""
    return balance.get_player_stats().get(stat_name, default)

def get_enemy_stat(enemy_type: str, stat_name: str, default: Any = None):
    """Accès rapide aux stats d'ennemi."""
    return balance.get_enemy_stats(enemy_type).get(stat_name, default)

def set_difficulty(level: str):
    """Change la difficulté globale."""
    return balance.set_difficulty(level)

def reload_balance():
    """Recharge la configuration d'équilibrage."""
    return balance.reload_config() 