import random
import os
import time
from models import spawn_hero, spawn_monster, GAME_DATA


def play_party_dungeon():
    # 1. Spawn the full party
    party = [
        spawn_hero("Sigurd", "Barbarian"),
        spawn_hero("Gimli", "Dwarf"),
        spawn_hero("Legolas", "Elf", chosen_spells=["Earth"]),
        spawn_hero("Gandalf", "Wizard", chosen_spells=["Fire", "Air", "Water"]),
    ]

    rooms_cleared = 0
    party_gold = 0

    while any(h.hp > 0 for h in party):
        # Spawn a new monster
        m_name = random.choice(list(GAME_DATA["monsters"].keys()))
        enemy = spawn_monster(m_name)
        enemy.x, enemy.y = 0, 1  # Adjacency fix

        while enemy.hp > 0 and any(h.hp > 0 for h in party):
            os.system("cls" if os.name == "nt" else "clear")
            print(f"--- ROOM {rooms_cleared + 1} | GOLD: {party_gold} ---")
            for h in party:
                print(
                    f"{h.name} ({h.char_class}): {h.hp} HP"
                    if h.hp > 0
                    else f"{h.name}: DEAD"
                )
            print(f"\nMONSTER: {enemy.char_class} (HP: {enemy.hp})")
            print("-" * 40)

            defending_heroes = []

            # HERO TURN
            for hero in party:
                if hero.hp <= 0 or enemy.hp <= 0:
                    continue
                hero.x, hero.y = 0, 0

                print(f"\n>> {hero.name}'s turn")
                action = input("[A] Attack  [D] Defend (+1 Die)  [S] Spell: ").upper()

                if action == "A":
                    hero.perform_attack(enemy)  #
                elif action == "D":
                    print(f"{hero.name} is defending!")
                    defending_heroes.append(hero)
                elif action == "S" and hero.spells:
                    print(f"Spells: {[s['name'] for s in hero.spells]}")
                    s_name = input("Cast: ")
                    hero.cast_spell(s_name)  #
                time.sleep(1)

            # MONSTER TURN
            if enemy.hp > 0 and any(h.hp > 0 for h in party):
                target = random.choice([h for h in party if h.hp > 0])
                print(
                    f"\n--- {enemy.char_class.upper()} ATTACKS {target.name.upper()}! ---"
                )

                original_defend = target.base_defend
                if target in defending_heroes:
                    target.base_defend += 1  #

                enemy.perform_attack(target)  #
                target.base_defend = original_defend
                input("\nPress Enter...")

        # 2. POST-COMBAT SEARCH PHASE
        if enemy.hp <= 0:
            rooms_cleared += 1
            print(f"\n*** {enemy.char_class} DEFEATED! ***")
            print("--- SEARCH PHASE: Each hero may search for treasure or traps ---")

            for hero in party:
                if hero.hp <= 0:
                    continue

                print(f"\n>> {hero.name}, will you search? ")
                choice = input("[Y] Search  [N] Skip: ").upper()

                if choice == "Y":
                    roll = random.randint(1, 6)
                    if roll == 1:
                        print("TRAP! A spear fires from the wall!")
                        hero.take_damage(1)  #
                    elif roll >= 5:
                        gold = random.randint(10, 50)
                        print(f"TREASURE! {hero.name} found {gold} gold!")
                        party_gold += gold
                    else:
                        print(f"{hero.name} found nothing of interest.")
                time.sleep(1)

            print(f"\nAdvancing to Room {rooms_cleared + 1}...")
            time.sleep(2)

    print(f"\nFINAL GOLD: {party_gold} | ROOMS: {rooms_cleared}")


if __name__ == "__main__":
    play_party_dungeon()
