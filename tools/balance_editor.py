#!/usr/bin/env python3
"""
Éditeur d'équilibrage simple pour Death Must Pygame.
Permet de modifier les paramètres de jeu facilement.
Usage: python tools/balance_editor.py
"""

import sys
import os
import json
from pathlib import Path

# Ajouter le répertoire parent au path pour importer game
sys.path.append(str(Path(__file__).parent.parent))

from game.balance_manager import BalanceManager

class BalanceEditor:
    def __init__(self):
        self.balance = BalanceManager()
        self.modified = False
    
    def main_menu(self):
        """Menu principal de l'éditeur."""
        while True:
            self.clear_screen()
            print("🎮 DEATH MUST PYGAME - Éditeur d'Équilibrage")
            print("=" * 60)
            print(self.balance.get_balance_summary())
            print("=" * 60)
            print("OPTIONS:")
            print("1. 👤 Modifier joueur")
            print("2. 👹 Modifier ennemis") 
            print("3. 🎯 Changer difficulté")
            print("4. 📊 Tests rapides")
            print("5. 💾 Sauvegarder")
            print("6. 🔄 Recharger")
            print("7. 🚀 Tester en jeu")
            print("8. ❌ Quitter")
            
            if self.modified:
                print("\n⚠️  Modifications non sauvegardées!")
            
            choice = input("\n👉 Choix: ").strip()
            
            if choice == "1":
                self.edit_player()
            elif choice == "2":
                self.edit_enemies()
            elif choice == "3":
                self.change_difficulty()
            elif choice == "4":
                self.quick_tests()
            elif choice == "5":
                self.save_config()
            elif choice == "6":
                self.reload_config()
            elif choice == "7":
                self.test_in_game()
            elif choice == "8":
                if self.confirm_quit():
                    break
            else:
                input("❌ Choix invalide. Appuyez sur Entrée...")
    
    def edit_player(self):
        """Menu d'édition du joueur."""
        while True:
            self.clear_screen()
            player = self.balance.get_player_stats()
            
            print("👤 ÉDITION JOUEUR")
            print("=" * 30)
            print(f"1. Dégâts d'attaque: {player.get('attack_damage', 'N/A')}")
            print(f"2. Points de vie: {player.get('max_hp', 'N/A')}")
            print(f"3. Vitesse: {player.get('speed', 'N/A')}")
            print(f"4. Portée d'attaque: {player.get('attack_range', 'N/A')}")
            print(f"5. Cooldown attaque: {player.get('attack_cooldown', 'N/A')}")
            print(f"6. Vitesse dash: {player.get('dash', {}).get('speed', 'N/A')}")
            print("7. 🔙 Retour")
            
            choice = input("\n👉 Modifier: ").strip()
            
            if choice == "1":
                self.edit_value("player.attack_damage", "Dégâts d'attaque", float)
            elif choice == "2":
                self.edit_value("player.max_hp", "Points de vie", int)
            elif choice == "3":
                self.edit_value("player.speed", "Vitesse", int)
            elif choice == "4":
                self.edit_value("player.attack_range", "Portée", int)
            elif choice == "5":
                self.edit_value("player.attack_cooldown", "Cooldown (secondes)", float)
            elif choice == "6":
                self.edit_value("player.dash.speed", "Vitesse dash", int)
            elif choice == "7":
                break
            else:
                input("❌ Choix invalide. Appuyez sur Entrée...")
    
    def edit_enemies(self):
        """Menu d'édition des ennemis."""
        while True:
            self.clear_screen()
            print("👹 ÉDITION ENNEMIS")
            print("=" * 30)
            
            enemies = list(self.balance.config.get("enemies", {}).keys())
            for i, enemy_type in enumerate(enemies, 1):
                stats = self.balance.get_enemy_stats(enemy_type)
                print(f"{i}. {enemy_type}: {stats.get('hp', 'N/A')} HP, {stats.get('damage', 'N/A')} dmg")
            
            print(f"{len(enemies) + 1}. 🔙 Retour")
            
            choice = input("\n👉 Modifier ennemi: ").strip()
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(enemies):
                    self.edit_enemy(enemies[idx])
                elif idx == len(enemies):
                    break
                else:
                    input("❌ Choix invalide. Appuyez sur Entrée...")
            except ValueError:
                input("❌ Veuillez entrer un numéro. Appuyez sur Entrée...")
    
    def edit_enemy(self, enemy_type: str):
        """Édition d'un type d'ennemi spécifique."""
        while True:
            self.clear_screen()
            stats = self.balance.config.get("enemies", {}).get(enemy_type, {})
            
            print(f"👹 ÉDITION {enemy_type.upper()}")
            print("=" * 30)
            print(f"1. HP: {stats.get('hp', 'N/A')}")
            print(f"2. Vitesse: {stats.get('speed', 'N/A')}")
            print(f"3. Dégâts: {stats.get('damage', 'N/A')}")
            print(f"4. Valeur XP: {stats.get('xp_value', 'N/A')}")
            print("5. 🔙 Retour")
            
            choice = input("\n👉 Modifier: ").strip()
            
            if choice == "1":
                self.edit_value(f"enemies.{enemy_type}.hp", "HP", int)
            elif choice == "2":
                self.edit_value(f"enemies.{enemy_type}.speed", "Vitesse", int)
            elif choice == "3":
                self.edit_value(f"enemies.{enemy_type}.damage", "Dégâts", int)
            elif choice == "4":
                self.edit_value(f"enemies.{enemy_type}.xp_value", "Valeur XP", int)
            elif choice == "5":
                break
            else:
                input("❌ Choix invalide. Appuyez sur Entrée...")
    
    def change_difficulty(self):
        """Changement de difficulté."""
        self.clear_screen()
        print("🎯 SÉLECTION DIFFICULTÉ")
        print("=" * 30)
        
        difficulties = list(self.balance.config.get("difficulty", {}).keys())
        current = self.balance.difficulty_level
        
        for i, diff in enumerate(difficulties, 1):
            marker = "👉" if diff == current else "  "
            multipliers = self.balance.config["difficulty"][diff]
            print(f"{marker} {i}. {diff.upper()}")
            print(f"     HP: x{multipliers.get('hp_multiplier', 1.0)}, "
                  f"Dmg: x{multipliers.get('damage_multiplier', 1.0)}, "
                  f"XP: x{multipliers.get('xp_multiplier', 1.0)}")
        
        choice = input(f"\n👉 Nouvelle difficulté (1-{len(difficulties)}): ").strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(difficulties):
                self.balance.set_difficulty(difficulties[idx])
                self.modified = True
                input("✅ Difficulté changée! Appuyez sur Entrée...")
            else:
                input("❌ Choix invalide. Appuyez sur Entrée...")
        except ValueError:
            input("❌ Veuillez entrer un numéro. Appuyez sur Entrée...")
    
    def quick_tests(self):
        """Tests d'équilibrage rapides."""
        self.clear_screen()
        print("📊 TESTS RAPIDES")
        print("=" * 30)
        print("1. 💪 Joueur plus fort (+50% dégâts)")
        print("2. 🛡️  Joueur plus résistant (+50% HP)")
        print("3. 👹 Ennemis plus forts (+30% HP)")
        print("4. ⚡ Jeu plus rapide (+50% vitesses)")
        print("5. 🎯 Reset aux valeurs par défaut")
        print("6. 🔙 Retour")
        
        choice = input("\n👉 Test: ").strip()
        
        if choice == "1":
            current = self.balance.get_value("player.attack_damage", 3)
            self.balance.set_value("player.attack_damage", current * 1.5)
            self.modified = True
        elif choice == "2":
            current = self.balance.get_value("player.max_hp", 10)
            self.balance.set_value("player.max_hp", current * 1.5)
            self.modified = True
        elif choice == "3":
            for enemy_type in self.balance.config.get("enemies", {}):
                current = self.balance.get_value(f"enemies.{enemy_type}.hp", 15)
                self.balance.set_value(f"enemies.{enemy_type}.hp", int(current * 1.3))
            self.modified = True
        elif choice == "4":
            # Augmenter toutes les vitesses
            current_player = self.balance.get_value("player.speed", 150)
            self.balance.set_value("player.speed", int(current_player * 1.5))
            for enemy_type in self.balance.config.get("enemies", {}):
                current = self.balance.get_value(f"enemies.{enemy_type}.speed", 80)
                self.balance.set_value(f"enemies.{enemy_type}.speed", int(current * 1.5))
            self.modified = True
        elif choice == "5":
            if input("⚠️  Confirmer reset? (o/N): ").lower() == 'o':
                self.balance._create_default_config()
                self.modified = True
        elif choice == "6":
            return
        
        if choice in ["1", "2", "3", "4", "5"]:
            input("✅ Test appliqué! Appuyez sur Entrée...")
    
    def edit_value(self, path: str, description: str, value_type):
        """Édition d'une valeur spécifique."""
        current = self.balance.get_value(path, "N/A")
        print(f"\n🔧 {description}")
        print(f"Valeur actuelle: {current}")
        
        new_value = input("Nouvelle valeur: ").strip()
        if new_value:
            try:
                converted_value = value_type(new_value)
                self.balance.set_value(path, converted_value)
                self.modified = True
                print(f"✅ {description} modifié: {current} → {converted_value}")
            except ValueError:
                print(f"❌ Valeur invalide pour {value_type.__name__}")
        
        input("Appuyez sur Entrée...")
    
    def save_config(self):
        """Sauvegarde la configuration."""
        if self.balance.save_config():
            self.modified = False
            input("✅ Configuration sauvegardée! Appuyez sur Entrée...")
        else:
            input("❌ Erreur de sauvegarde! Appuyez sur Entrée...")
    
    def reload_config(self):
        """Rechargement de la configuration."""
        if self.modified:
            confirm = input("⚠️  Perdre les modifications? (o/N): ")
            if confirm.lower() != 'o':
                return
        
        if self.balance.reload_config():
            self.modified = False
            input("✅ Configuration rechargée! Appuyez sur Entrée...")
        else:
            input("❌ Erreur de rechargement! Appuyez sur Entrée...")
    
    def test_in_game(self):
        """Lance le jeu pour tester."""
        if self.modified:
            print("⚠️  Il y a des modifications non sauvegardées.")
            choice = input("1. Sauvegarder et tester\n2. Tester sans sauvegarder\n3. Annuler\n👉 Choix: ")
            
            if choice == "1":
                self.balance.save_config()
                self.modified = False
            elif choice == "3":
                return
        
        print("🚀 Lancement du jeu...")
        try:
            import subprocess
            subprocess.run([sys.executable, "-m", "game.main"], cwd=Path(__file__).parent.parent)
        except Exception as e:
            print(f"❌ Erreur lancement: {e}")
            input("Appuyez sur Entrée...")
    
    def confirm_quit(self):
        """Confirmation de sortie."""
        if self.modified:
            print("⚠️  Modifications non sauvegardées!")
            return input("Quitter sans sauvegarder? (o/N): ").lower() == 'o'
        return True
    
    def clear_screen(self):
        """Efface l'écran."""
        os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Point d'entrée principal."""
    try:
        editor = BalanceEditor()
        editor.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir!")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        input("Appuyez sur Entrée pour quitter...")

if __name__ == "__main__":
    main() 