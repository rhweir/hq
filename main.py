from models import spawn_hero, spawn_monster
from map import Map
import time


def start_game():
    # 1. Setup Map
    game_map = Map()

    # 2. Spawn your Hero (The Wizard needs his spells!)
    # We'll put him at x=1, y=1
    player = spawn_hero(
        "Gandalf", "Wizard", x=1, y=1, chosen_spells=["Fire", "Earth", "Air"]
    )

    # 3. Spawn a test monster at x=5, y=5
    goblin = spawn_monster("Goblin", x=5, y=5)

    heroes = [player]
    monsters = [goblin]

    # 4. THE MAIN LOOP
    while True:
        game_map.render(heroes, monsters)

        print(f"\n--- {player.name}'s Turn ---")
        print(f"HP: {player.hp} | MP: {player.mp}")
        print(f"Spells: {[s['name'] for s in player.spells]}")

        cmd = input("\nCommand (w/a/s/d to move, 'c' to cast, 'q' to quit): ").lower()

        if cmd == "q":
            break
        elif cmd in ["w", "a", "s", "d"]:
            # Basic movement logic
            if cmd == "w":
                player.y -= 1
            if cmd == "s":
                player.y += 1
            if cmd == "a":
                player.x -= 1
            if cmd == "d":
                player.x += 1
        elif cmd == "c":
            spell_name = input("Enter spell name: ")
            player.cast_spell(spell_name)
            time.sleep(2)  # Pause so you can see the message


if __name__ == "__main__":
    start_game()
