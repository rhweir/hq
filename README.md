# HeroQuest TUI (UK Edition)

## A terminal-based Text User Interface (TUI) recreation of the 1989 classic dungeon crawler. This project implements the core mechanics of the HeroQuest UK Edition, featuring a 26x19 grid and a complete elemental magic system.

## Features

Authentic Grid: Implements the 26x19 board dimensions of the original UK release.

Elemental Magic: Full spell decks for Air, Earth, Fire, and Water categorized within the game data.

Entity Management: Dedicated classes for Heroes and Monsters with attribute inheritance.

Spellcaster Logic: Automatic spell assignment for classes flagged with "is_spellcaster" (Wizard and Elf).

Robust Casting: Spellcasting logic includes validation checks and discard-after-use mechanics.

## Project Structure

main.py: Entry point containing the game loop and terminal rendering triggers.

models.py: Core logic for the Entity, Hero, and Monster classes, including the spawn and cast_spell methods.

map.py: Handles the 2D coordinate system and ASCII rendering of the board.

data.py: Facilitates the loading of GAME_DATA from the JSON source.

gamedata.json: The primary data store for hero stats, monster attributes, and spell definitions.

## Setup and Execution
### Prerequisites

Python 3.10 or higher.

A terminal supporting standard clear commands (Linux, macOS, or Windows Terminal).

## Running the Project
```Bash
python main.py
```

## Controls

W/A/S/D: Movement across the x and y axes.

C: Initiate the cast_spell method.

Q: Terminate the game session.

