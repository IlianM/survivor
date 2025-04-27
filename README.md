# Death Must Pygame

**Reincarnation of the unkillable last human against all gods**

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation & Dependencies](#installation--dependencies)
5. [Running the Game](#running-the-game)
6. [Controls](#controls)
7. [Gameplay Mechanics](#gameplay-mechanics)
8. [Code Architecture](#code-architecture)
9. [Assets & Licensing](#assets--licensing)
---

## Project Overview
*Death Must Pygame* is a top-down action game built with Python and Pygame. You play as the last human, fighting endless waves of goblins with dynamic scaling difficulty, leveling up, and choosing upgrades.

## Features
- **Dynamic Enemy Scaling**: Enemies spawn with varying tiers (normal, rare, elite), scaling HP and speed.
- **Player Progression**: Gain XP orbs, level up, and choose upgrades from a menu.
- **Auto-Attack & Manual Attack**: Toggle auto-attack or aim with the mouse.
- **Camera & Tiled Background**: Smooth scrolling camera and tiled map.
- **Sound & Music**: Background music and SFX for attacks, pickups, and level-ups.
- **Game Over Summary**: Displays survival time, level, and kill count.

## Project Structure
```
death_must_pygame/
│
├─ assets/            # Sprites and menus
│   ├─ knight1.png
│   ├─ knight2.png
│   ├─ knight3.png
│   ├─ knight_up1.png
│   ├─ knight_up2.png
│   ├─ knightdown_1.png
│   ├─ knightdown_2.png
│   ├─ slash.png
│   ├─ gobelin-right.png
│   ├─ gobelin-left.png
│   ├─ background.png
│   └─ main_menu.png
│
├─ fx/                # Sound effects and music
│   ├─ attack.mp3
│   ├─ levelup.mp3
│   ├─ xp_orb.mp3
│   └─ background_music.mp3
│
├─ settings.py        # Global constants (window size, map size, FPS)
├─ main.py            # Main game loop, menus, and state management
├─ player.py          # Player class: movement, animations, attacks, progression
├─ enemy.py           # Enemy class: tiers, scaling, movement, flash/tint effects
├─ xp_orb.py          # XPOrb class: orbs behavior and pickup logic
└─ README.md          # This documentation file
```

## Installation & Dependencies
1. **Python 3.13+**
2. **Pygame 2.6+**

Install dependencies with:
```bash
pip install pygame
```

## Running the Game
From the project root:
```bash
python main.py
```

## Controls
- **Z/Q/S/D**: Move Up/Left/Down/Right
- **Left Mouse Button**: Manual attack toward mouse cursor
- **Y**: Toggle auto-attack (targets nearest enemy automatically)
- **K**: Open upgrade menu if skill points available
- **ESC / Close Window**: Quit game

## Gameplay Mechanics
- **Attacks**: Deal damage in a cone; auto-attacks target nearest enemy.
- **XP & Leveling**: Defeat enemies to spawn XP orbs; pick them up to gain XP.
- **Upgrade Menu**: On leveling up, choose from 3 random upgrades (e.g., Strength Boost, Haste).
- **Enemy Spawn**: Frequency and tier probabilities adjust over time and player level.
- **Game Over**: When HP ≤ 0, shows survival time, final level, and kill count.

## Code Architecture
- **settings.py**: Configuration constants.
- **main.py**: Initializes Pygame, handles game states (menu, play, upgrade, game over), spawns enemies, updates/draws all entities.
- **player.py**: Handles player stats, input, movement, animations, attack logic, and leveling.
- **enemy.py**: Defines Enemy behavior: scaling, movement toward player, separation, drawing with tints and flashes.
- **xp_orb.py**: Defines XPOrb: attraction mechanics and pickup sound.

## Assets & Licensing
- All sprites and audio assets are placed in `assets/` and `fx/`.
- Ensure you have the rights for any third-party assets you include.

