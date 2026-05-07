# ECHO HUNT

ECHO HUNT is a Python + pygame-ce pseudo-isometric arcade survival game built for the LIM2 IA Game Challenge.

Selected track: **Track 2 - Smart Pursuit**. The player is controlled in real time while multiple enemies use A* pathfinding to chase and intercept them across a procedural grid with static and dynamic obstacles.

## Setup

1. Clone the repository:

```bash
git clone <repo-url>
cd echo_hunt
```

2. Create and activate a Python virtual environment:

Windows PowerShell:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt:
```cmd
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Run

With the virtual environment active, start the game:

```bash
python main.py
```

## Controls

- Enter: start from menu, restart after game over
- WASD, ZQSD, or Arrow Keys: move, depending on Windows language/keyboard layout
- Left Shift: sprint
- Space: dash
- Tab: maximize or minimize the minimap
- Esc: pause or resume
- R: restart after game over
- M: return to main menu from pause or game over
- Q: quit the game
- T: hide or show the first-sector tutorial

Menu, pause, and game-over screens also include clickable buttons. Use the `SHORTCUTS` button in the main or pause menu to view the full key list in-game, including the detected movement layout and arrow-key alternatives.

Before starting, click the player name field on the main menu and type your name. Scores are saved with that name.
- In the main menu, open `SETTINGS` to mute or unmute background music and sound effects independently.
- In `SETTINGS`, use the `+` and `-` buttons to adjust music and SFX volume.
- The pause menu now also includes a `SETTINGS` button so you can adjust audio without leaving the game.
## Gameplay

The goal is pure evasion. There is no direct combat. Survive as long as possible, reach the sector exit, and avoid hunters, hazards, and moving wall obstacles.

The screen displays:

- enemy A* paths in real time
- enemy state, explored nodes, path length, and recalculation interval
- threat level
- hearts, stamina, sector, timer, FPS, and a toggleable minimap
- first-sector tutorial hints
- a first-level safety tutorial: hunters and hazards can hurt you and show coaching tips, but they cannot kill you before level 2
- synthwave scanline/noise effect for arcade atmosphere
- high-score board with player name, maximum level reached, and survival time

## AI Architecture

The AI module is separated from game rendering and presentation:

- `ai/astar.py` contains the reusable A* search implementation.
- `ai/enemy_brain.py` converts game state into AI decisions and throttles path recalculation.
- `entities/enemy.py` owns enemy updates but does not render paths or UI.
- `rendering/renderer.py` only visualizes the current paths and debug metrics.

A* input is a grid plus start and goal positions. Its output is a list of grid cells forming the path. The game reads debug metrics such as explored nodes and path length for display only.

## A* Heuristic

ECHO HUNT uses Manhattan distance:

```text
abs(x1 - x2) + abs(y1 - y2)
```

This matches the movement model because navigation uses four grid directions: up, down, left, and right. Diagonal movement is not used by the pathfinder, so Manhattan distance is admissible for this grid.

## Dynamic Obstacles

Each sector adds a set of moving wall obstacles. They update on a fixed timer, never every frame. Obstacles avoid the player spawn, sector exit, and enemy starting cells, and each placement is validated so the spawn-to-exit route remains traversable.

Difficulty increases every level:

- enemies move faster
- enemies detect the player from farther away
- A* path recalculation becomes more aggressive
- more moving obstacles appear
- extra hunters appear in later levels

The exit is placed far from the spawn and marked by a bright green tile plus an `EXIT` beacon so the player always knows where the next level begins.

## Tests

```bash
python -m pytest -q
```

Covered scenarios include:

- A* simple path
- A* no-path and invalid-grid cases
- procedural sector traversability
- dynamic obstacles preserving spawn, exit, and route validity
- keyboard layout labels for French/AZERTY and English/German layouts
- high-score sorting
- dash stamina and cooldown behavior
- damage invulnerability
- menu, pause, and game-over restart transitions
- save/progression roundtrip

## Demo Checklist

1. Launch with `python main.py`.
2. Press Enter from the menu.
3. Type a player name, then start the run.
4. Move with the displayed controls, sprint with Left Shift, and dash with Space.
5. Point out enemy paths and AI debug stats while enemies pursue the player.
6. Use the first-sector tutorial checklist to explain win and lose conditions.
7. Reach the bright `EXIT` beacon to advance to a harder level.
8. Pause with Esc, then use Resume, Main Menu, or Quit.
9. Touch hazards or enemies to demonstrate damage and invulnerability.
10. Let the player die and show the high-score board.

## Dependencies

- pygame-ce
- numpy
- pytest
