import random
import os
import time
import json
import sys
from collections import Counter
from models import spawn_hero, spawn_monster, GAME_DATA


# --- 1. PERSISTENCE (SAVE/LOAD) ---
def save_game(party, gold, dungeon_num, inventory):
    """Saves party state, ensuring weapon names are preserved."""
    save_data = {
        "gold": gold,
        "dungeon_num": dungeon_num,
        "inventory": inventory,
        "party": [
            {
                "name": h.name,
                "class": h.char_class,
                "hp": h.hp,
                "mp": h.mp,
                "weapon_name": h.primary_weapon.get("name", "Unarmed"),
                "slots": h.slots,
                "spells": h.spells,
            }
            for h in party
        ],
    }
    with open("savegame.json", "w") as f:
        json.dump(save_data, f, indent=4)
    print("\n[GAME SAVED]")


def load_game():
    """Loads game and re-links weapon dictionaries to restore ATK stats."""
    if not os.path.exists("savegame.json"):
        return None
    try:
        with open("savegame.json", "r") as f:
            data = json.load(f)
        party = []
        for h_d in data["party"]:
            h = spawn_hero(h_d["name"], h_d["class"])
            h.hp, h.mp, h.slots, h.spells = (
                h_d["hp"],
                h_d["mp"],
                h_d["slots"],
                h_d["spells"],
            )
            # Restore full weapon stats from library
            w_name = h_d.get("weapon_name", "Unarmed")
            h.primary_weapon = GAME_DATA["weapons"].get(
                w_name, GAME_DATA["weapons"]["Unarmed"]
            )
            h.primary_weapon["name"] = w_name
            party.append(h)
        return party, data["gold"], data["dungeon_num"], data.get("inventory", [])
    except:
        return None


# --- 2. UI HELPERS ---
def format_inventory(inventory):
    """Displays items as 'Name xCount'."""
    if not inventory:
        return "Empty"
    counts = Counter(inventory)
    return ", ".join([f"{name} x{qty}" for name, qty in counts.items()])


def display_party_status(party, gold, inventory):
    """Full HUD with HP/MP current/max, ATK/DEF, and Gear."""
    print(f"\n{'='*95}")
    print(
        f"--- PARTY STATUS | GOLD: {gold} | INVENTORY: {format_inventory(inventory)} ---"
    )
    print(f"{'='*95}")
    print(
        f"{'NAME':10} | {'CLASS':10} | {'HP':7} | {'MP':7} | {'ATK':3} | {'DEF':3} | {'EQUIPMENT'}"
    )
    print("-" * 95)

    for h in party:
        base = GAME_DATA["heroes"].get(h.char_class, {})
        m_hp, m_mp = base.get("hp", 0), base.get("mp", 0)
        atk = h.calculate_attack_dice()
        dfe = h.calculate_defence_dice()

        weap = h.primary_weapon.get("name", "Unarmed")
        armour = [
            v.get("name", k.title()) for k, v in h.slots.items() if v.get("cost", 0) > 0
        ]
        equip_str = f"{weap} | " + (", ".join(armour) if armour else "No Armour")

        hp_display = f"{h.hp}/{m_hp}" if h.hp > 0 else "DEAD"
        print(
            f"{h.name:10} | {h.char_class:10} | {hp_display:7} | {h.mp}/{m_mp:2} | {atk:3} | {dfe:3} | {equip_str}"
        )
    print(f"{'='*95}\n")


# --- 3. COMBAT & GROUP SEARCH ---
def resolve_combat(party, enemy, gold, inventory):
    """Combat with immediate gold rewards upon monster death."""
    enemy.x, enemy.y = 0, 1
    for h in party:
        h.x, h.y = 0, 0

    while enemy.hp > 0 and any(h.hp > 0 for h in party):
        os.system("cls" if os.name == "nt" else "clear")
        display_party_status(party, gold, inventory)
        print(f"BATTLE: {enemy.char_class.upper()} (HP: {enemy.hp})")
        defending = []

        for h in party:
            if h.hp <= 0 or enemy.hp <= 0:
                continue
            turn_active = True
            while turn_active:
                print(f"\n>> {h.name}'s Turn")
                choice = input("[A]ttack [D]efend [I]tem: ").upper()
                if choice == "A":
                    h.perform_attack(enemy)
                    turn_active = False
                elif choice == "D":
                    defending.append(h)
                    turn_active = False
                elif choice == "I":
                    if not inventory:
                        print("No items!")
                        time.sleep(1)
                        continue
                    uniques = list(set(inventory))
                    for idx, itm in enumerate(uniques):
                        print(f"[{idx+1}] {itm}")
                    sel = input("Use item # (B for back): ")
                    if sel.upper() == "B":
                        continue
                    try:
                        itm_name = uniques[int(sel) - 1]
                        inventory.remove(itm_name)
                        if itm_name == "Potion of Healing":
                            print("\nTarget:")
                            for i, t in enumerate(party):
                                print(f"[{i+1}] {t.name}")
                            target = party[int(input("Hero #: ")) - 1]
                            heal = random.randint(1, 6)
                            target.hp = min(
                                GAME_DATA["heroes"][target.char_class]["hp"],
                                target.hp + heal,
                            )
                            print(f"{target.name} healed for {heal} HP!")
                            turn_active = False
                    except:
                        pass
            time.sleep(1)

        if enemy.hp <= 0:
            bounty = random.randint(10, 30)
            gold += bounty
            print(f"\n{enemy.char_class} defeated! Found {bounty} gold.")
            time.sleep(1.5)
            break

        if enemy.hp > 0:
            target = random.choice([h for h in party if h.hp > 0])
            orig_def = target.base_defend
            if target in defending:
                target.base_defend += 1
            enemy.perform_attack(target)
            target.base_defend = orig_def
            input("\nPress Enter...")

    if enemy.hp <= 0 and any(h.hp > 0 for h in party):
        if input("\nSearch room as a party? (Y/N): ").upper() == "Y":
            roll = random.randint(1, 6)
            if roll == 1:
                victim = random.choice([h for h in party if h.hp > 0])
                print(f"TRAP! {victim.name} takes 1 damage!")
                victim.take_damage(1)
            elif roll == 6:
                print("TREASURE! Found a Potion of Healing!")
                inventory.append("Potion of Healing")
            elif roll >= 4:
                g = random.randint(30, 80)
                gold += g
                print(f"TREASURE! Found {g} gold!")
            else:
                print("The room is empty.")
            input("\nPress Enter...")
    return gold, inventory


# --- 4. TOWN HUB & SHOP ---
def shop_menu(party, gold, inventory):
    """Shop including Buy and 50% Sell-back logic."""
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        display_party_status(party, gold, inventory)
        print("=== BLACKSMITH SHOP ===")
        print("1. Buy Weapons | 2. Buy Armour | 3. Sell Items | 4. Back")
        choice = input("\nChoice: ")
        if choice == "4":
            break

        if choice == "3":  # SELL MODE
            sell_opts = []
            for item in set(inventory):
                val = GAME_DATA["items"].get(item, {}).get("cost", 0) // 2
                if val > 0:
                    sell_opts.append({"n": item, "t": "i", "v": val})
            for h in party:
                w_n = h.primary_weapon.get("name")
                if w_n and w_n != "Unarmed":
                    val = GAME_DATA["weapons"].get(w_n, {}).get("cost", 0) // 2
                    sell_opts.append(
                        {"n": f"{h.name}'s {w_n}", "t": "w", "h": h, "v": val}
                    )
                for s, d in h.slots.items():
                    a_n = d.get("name")
                    if a_n and a_n != "Empty":
                        val = GAME_DATA["armour"].get(a_n, {}).get("cost", 0) // 2
                        sell_opts.append(
                            {
                                "n": f"{h.name}'s {a_n}",
                                "t": "a",
                                "h": h,
                                "s": s,
                                "v": val,
                            }
                        )

            if not sell_opts:
                print("Nothing to sell!")
                time.sleep(1)
                continue
            for i, o in enumerate(sell_opts):
                print(f"[{i+1}] {o['n']} (+{o['v']}g)")
            sel = input("\nSell # (B to back): ")
            if sel.upper() == "B":
                continue
            try:
                it = sell_opts[int(sel) - 1]
                gold += it["v"]
                if it["t"] == "i":
                    inventory.remove(it["n"])
                elif it["t"] == "w":
                    it["h"].primary_weapon = GAME_DATA["weapons"]["Unarmed"]
                elif it["t"] == "a":
                    it["h"].slots[it["s"]] = GAME_DATA["armour"]["Empty"]
                print("Sold!")
                time.sleep(1)
            except:
                pass
            continue

        cat = "weapons" if choice == "1" else "armour"
        items = [(n, d) for n, d in GAME_DATA.get(cat, {}).items() if n != "Empty"]
        for i, (name, d) in enumerate(items):
            print(f"[{i+1}] {name:15} | {d['cost']}g")
        sel = input("\nBuy # (B to back): ")
        if sel.upper() == "B":
            continue
        try:
            name, data = items[int(sel) - 1]
            hero = party[int(input("Assign to Hero #: ")) - 1]
            if gold >= data["cost"]:
                if hero.char_class == "Wizard" and not data.get("wizard_ok", True):
                    print("Wizard cannot equip this!")
                    time.sleep(1)
                    continue
                gold -= data["cost"]
                data["name"] = name
                if cat == "weapons":
                    hero.primary_weapon = data
                else:
                    hero.slots[data["slot"]] = data
            else:
                print("Need more gold!")
            time.sleep(1)
        except:
            pass
    return gold


def town_hub(party, gold, dungeon_num, inventory):
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        display_party_status(party, gold, inventory)
        print(f"--- TOWN HUB | DUNGEON {dungeon_num} ---")
        print("[H]eal All (50g) [R]esurrect (200g) [S]hop [V] Save [Q]uit [C]ontinue")
        act = input("\nAction: ").upper()
        if act == "H" and gold >= 50:
            gold -= 50
            for h in party:
                if h.hp > 0:
                    h.hp = GAME_DATA["heroes"][h.char_class]["hp"]
        elif act == "R" and gold >= 200:
            for h in party:
                if h.hp <= 0:
                    h.hp = GAME_DATA["heroes"][h.char_class]["hp"]
                    gold -= 200
                    break
        elif act == "S":
            gold = shop_menu(party, gold, inventory)
        elif act == "V":
            save_game(party, gold, dungeon_num, inventory)
        elif act == "Q":
            save_game(party, gold, dungeon_num, inventory)
            sys.exit()
        elif act == "C":
            return party, gold, dungeon_num, inventory


# --- 5. MAIN LOOP ---
def main():
    loaded = load_game()
    if loaded:
        party, gold, dungeon_num, inventory = loaded
    else:
        party = [
            spawn_hero("Sigurd", "Barbarian"),
            spawn_hero("Gimli", "Dwarf"),
            spawn_hero("Legolas", "Elf", ["Earth"]),
            spawn_hero("Gandalf", "Wizard", ["Fire"]),
        ]
        gold, dungeon_num, inventory = 100, 1, []

    while any(h.hp > 0 for h in party):
        party, gold, dungeon_num, inventory = town_hub(
            party, gold, dungeon_num, inventory
        )
        rooms = 5 + (dungeon_num * 5)
        deck = (["monster"] * int(rooms * 0.6)) + (["empty"] * int(rooms * 0.4))
        random.shuffle(deck)
        for i, card in enumerate(deck):
            if not any(h.hp > 0 for h in party):
                break
            os.system("cls" if os.name == "nt" else "clear")
            display_party_status(party, gold, inventory)
            print(
                f"ROOM {i+1}/{rooms}: {'Monster attacks!' if card == 'monster' else 'Empty.'}"
            )
            if card == "monster":
                m_type = random.choice(list(GAME_DATA["monsters"].keys()))
                gold, inventory = resolve_combat(
                    party, spawn_monster(m_type), gold, inventory
                )
            else:
                time.sleep(1)
        if any(h.hp > 0 for h in party):
            dungeon_num += 1


if __name__ == "__main__":
    main()
