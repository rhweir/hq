import random
import os
import time
from models import spawn_hero, spawn_monster, GAME_DATA


def play_dungeon():
    # 1. Initialization
    player = spawn_hero("Sigurd", "Barbarian")
    victory_count = 0
    player.x, player.y = 0, 0  # Adjacency fix for models.py

    print("--- STARTING THE DUNGEON RUN ---")
    time.sleep(1)

    # 2. Outer Loop: Spawns new monsters until player dies
    while player.hp > 0:
        m_name = random.choice(list(GAME_DATA["monsters"].keys()))
        enemy = spawn_monster(m_name)
        enemy.x, enemy.y = 0, 1  # Ensure adjacency for every new spawn

        # 3. Inner Loop: The individual encounter
        while enemy.hp > 0 and player.hp > 0:
            os.system("cls" if os.name == "nt" else "clear")

            print(f"DUNGEON PROGRESS: {victory_count} Monsters Slain")
            print("=" * 34)
            print(f"      POV ENCOUNTER: {enemy.char_class.upper()}")
            print("=" * 34)
            print(f" {player.name} HP: {player.hp} | MP: {player.mp}")
            print(
                f" {enemy.char_class} HP: {enemy.hp} | ATK: {enemy.calculate_attack_dice()}"
            )
            print("-" * 34)
            print(" [A] Attack (Left)    [D] Defend (Right)")
            print(" [W] Search (Up)      [S] Spell  (Down)")
            print("-" * 34)

            choice = input("\nYour decision: ").upper()

            if choice == "A":
                player.perform_attack(enemy)  #
                if enemy.hp > 0:
                    print(f"\nThe {enemy.char_class} counter-attacks!")
                    enemy.perform_attack(player)

            elif choice == "D":
                print(f"\nYou block! The {enemy.char_class} strikes your shield.")
                # We reuse the perform_attack logic but could add defense buffs here
                enemy.perform_attack(player)

            elif choice == "S":
                if not player.spells:
                    print(f"\n{player.char_class}s have no magic!")
                else:
                    spell_choice = input(f"Cast {[s['name'] for s in player.spells]}: ")
                    player.cast_spell(spell_choice)  #
                    if enemy.hp > 0:
                        enemy.perform_attack(player)

            elif choice == "W":
                print("\nYou search the room...")
                if random.randint(1, 6) >= 5:
                    print("Found a Potion! (HP +2)")
                    player.hp = min(8, player.hp + 2)
                else:
                    print("You found nothing and got ambushed!")
                    enemy.perform_attack(player)

            input("\nPress Enter...")

        # 4. Victory Check
        if enemy.hp <= 0:
            victory_count += 1
            print(f"\n*** {enemy.char_class} DEFEATED! ***")
            print("You catch your breath before moving to the next room...")
            time.sleep(2)

    # 5. Final Death Screen
    print("\n" + "!" * 34)
    print(f"  GAME OVER: YOU DIED AT ROOM {victory_count + 1}")
    print("!" * 34)


if __name__ == "__main__":
    play_dungeon()
