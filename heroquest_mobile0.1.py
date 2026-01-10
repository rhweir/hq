import random
import os
import time
import json
import sys
from collections import Counter
from models import spawn_hero, spawn_monster, GAME_DATA


# --- 1. PERSISTENCE ---
def save_game(party, gold, dungeon_num, inventory):
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
def display_party_status(party, gold, inventory, room_idx=None, total_rooms=None):
    """Full HUD with Health, Equipment, and Dungeon Progress Bar."""
    os.system("cls" if os.name == "nt" else "clear")

    # Progress Bar Calculation
    progress_ui = ""
    if room_idx is not None and total_rooms is not None:
        bar_length = 20
        filled = int((room_idx / total_rooms) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        percent = int((room_idx / total_rooms) * 100)
        progress_ui = f"PROGRESS: [{bar}] {percent}%"

    print(f"\n{'='*95}")
    print(f"{progress_ui:45} | GOLD: {gold:5} | INV: {len(inventory)} items")
    print(f"{'='*95}")
    print(
        f"{'NAME':10} | {'CLASS':10} | {'HP':7} | {'MP':7} | {'ATK':3} | {'DEF':3} | {'EQUIPMENT'}"
    )
    print("-" * 95)
    for h in party:
        base = GAME_DATA["heroes"].get(h.char_class, {})
        m_hp, m_mp = base.get("hp", 0), base.get("mp", 0)
        atk, dfe = h.calculate_attack_dice(), h.calculate_defence_dice()
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


# --- 3. COMBAT & EXPLORATION ---
def resolve_combat(party, enemy, gold, inventory, dungeon_num, r_idx, r_total):
    enemy.x, enemy.y = 0, 1
    for h in party:
        h.x, h.y = 0, 0
    while enemy.hp > 0 and any(h.hp > 0 for h in party):
        display_party_status(party, gold, inventory, r_idx, r_total)
        print(f"BATTLE: {enemy.char_class.upper()} (HP: {enemy.hp})")
        defending = []
        for h in party:
            if h.hp <= 0 or enemy.hp <= 0:
                continue
            action_taken = False
            while not action_taken:
                print(f"\n>> {h.name}'s Turn")
                choice = input("[A]ttack [D]efend [I]tem: ").upper()
                if choice == "A":
                    h.perform_attack(enemy)
                    action_taken = True
                elif choice == "D":
                    defending.append(h)
                    action_taken = True
                elif choice == "I":
                    if not inventory:
                        print("No items!")
                        time.sleep(1)
                        continue
                    uniques = list(set(inventory))
                    for idx, itm in enumerate(uniques):
                        print(f"[{idx+1}] {itm}")
                    sel = input("Use item # (B for back): ")
                    if sel.upper() != "B":
                        try:
                            itm_name = uniques[int(sel) - 1]
                            if itm_name == "Potion of Healing":
                                print("\nTarget:")
                                for i, t in enumerate(party):
                                    print(f"[{i+1}] {t.name}")
                                target = party[int(input("Hero #: ")) - 1]
                                inventory.remove(itm_name)
                                heal = random.randint(1, 6)
                                target.hp = min(
                                    GAME_DATA["heroes"][target.char_class]["hp"],
                                    target.hp + heal,
                                )
                                print(f"{target.name} healed for {heal} HP!")
                                action_taken = True
                        except:
                            pass
        if enemy.hp <= 0:
            base_reward = (enemy.calculate_attack_dice() * 5) + (enemy.hp // 2)
            bounty = random.randint(base_reward, base_reward + (dungeon_num * 10))
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
    return gold, inventory


# --- 4. SHOP & TOWN ---
def shop_menu(party, gold, inventory):
    while True:
        display_party_status(party, gold, inventory)
        print("=== SHOP: 1.Buy Weap | 2.Buy Arm | 3.Sell Items | 4.Back ===")
        choice = input("\nChoice: ")
        if choice == "4":
            break

        if choice == "3":  # BULK SELL
            while True:
                display_party_status(party, gold, inventory)
                print("--- SELL ITEMS (50% Value) ---")
                sell_opts = []
                inv_counts = Counter(inventory)
                for item, count in inv_counts.items():
                    val = GAME_DATA["items"].get(item, {}).get("cost", 0) // 2
                    if val > 0:
                        sell_opts.append({"n": item, "t": "i", "v": val, "qty": count})
                for h in party:
                    if h.primary_weapon.get("name") != "Unarmed":
                        w_n = h.primary_weapon["name"]
                        val = GAME_DATA["weapons"].get(w_n, {}).get("cost", 0) // 2
                        sell_opts.append(
                            {"n": f"{h.name}'s {w_n}", "t": "w", "h": h, "v": val}
                        )
                if not sell_opts:
                    print("Nothing to sell!")
                    time.sleep(1)
                    break
                for i, o in enumerate(sell_opts):
                    q = f" (x{o['qty']})" if "qty" in o else ""
                    print(f"[{i+1}] {o['n']}{q} (+{o['v']}g each)")
                sel = input("\nSell # (B to finish): ")
                if sel.upper() == "B":
                    break
                try:
                    it = sell_opts[int(sel) - 1]
                    if it["t"] == "i" and it["qty"] > 1:
                        amt = input(f"Sell [1] or [A]ll {it['n']}? ").upper()
                        num = it["qty"] if amt == "A" else 1
                        for _ in range(num):
                            inventory.remove(it["n"])
                            gold += it["v"]
                    else:
                        gold += it["v"]
                        if it["t"] == "i":
                            inventory.remove(it["n"])
                        elif it["t"] == "w":
                            it["h"].primary_weapon = GAME_DATA["weapons"]["Unarmed"]
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
            print("\nAssign to which Hero?")
            for i, h in enumerate(party):
                print(f"[{i+1}] {h.name} ({h.char_class})")
            hero = party[int(input("Hero #: ")) - 1]
            if gold >= data["cost"]:
                if hero.char_class == "Wizard" and not data.get("wizard_ok", True):
                    print("Wizard restricted!")
                    time.sleep(1)
                    continue
                gold -= data["cost"]
                data["name"] = name
                if cat == "weapons":
                    hero.primary_weapon = data
                else:
                    hero.slots[data["slot"]] = data
            else:
                print("Not enough gold!")
        except:
            pass
    return gold


def town_hub(party, gold, dungeon_num, inventory):
    while True:
        display_party_status(party, gold, inventory)
        print(f"--- TOWN HUB | DUNGEON {dungeon_num} ---")
        print("[H]eal(50g) [R]esurrect(200g) [S]hop [V]Save [Q]uit [C]ontinue")
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
        rooms_total = 5 + (dungeon_num * 5)
        deck = (["monster"] * int(rooms_total * 0.6)) + (
            ["empty"] * int(rooms_total * 0.4)
        )
        random.shuffle(deck)

        for i, card in enumerate(deck):
            if not any(h.hp > 0 for h in party):
                break

            # Progress tracking
            display_party_status(party, gold, inventory, i, rooms_total)
            penalty = int(gold * 0.10)

            choice = input(
                f"[E]xplore or [R]etreat to Town ({penalty}G Penalty): "
            ).upper()
            if choice == "R":
                gold -= penalty
                print(f"Retreated! Paid {penalty}G penalty.")
                time.sleep(2)
                break

            if card == "monster":
                m_type = random.choice(list(GAME_DATA["monsters"].keys()))
                gold, inventory = resolve_combat(
                    party,
                    spawn_monster(m_type),
                    gold,
                    inventory,
                    dungeon_num,
                    i,
                    rooms_total,
                )
            else:
                print("The room is empty.")
                time.sleep(1)

            if i == len(deck) - 1:
                display_party_status(party, gold, inventory, rooms_total, rooms_total)
                print("\nDUNGEON CLEARED!")
                dungeon_num += 1
                time.sleep(2)


if __name__ == "__main__":
    main()
