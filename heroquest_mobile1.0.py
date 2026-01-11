import random
import os
import time
import json


# --- GRUVBOX COLOR PALETTE ---
class Col:
    HDR = "\033[1;36m"  # Aqua
    HPG = "\033[1;32m"  # Gruv Green
    HPR = "\033[1;31m"  # Gruv Red
    GLD = "\033[1;33m"  # Gruv Yellow
    EQU = "\033[1;34m"  # Gruv Blue
    MAG = "\033[1;35m"  # Gruv Purple
    RST = "\033[0m"  # Reset
    BOLD = "\033[1m"


SCREEN_WIDTH = 60  # Slightly wider for laptop


def center(text, color=Col.RST):
    padding = max(0, (SCREEN_WIDTH - len(text)) // 2)
    return f"{' ' * padding}{color}{text}{Col.RST}"


# --- 1. DATA ---
GAME_DATA = {
    "heroes": {
        "Barbarian": {"hp": 8, "atk": 3, "def": 2, "spells": []},
        "Dwarf": {"hp": 7, "atk": 2, "def": 2, "spells": []},
        "Elf": {"hp": 6, "atk": 2, "def": 2, "spells": ["Sleep", "Heal"]},
        "Wizard": {
            "hp": 4,
            "atk": 1,
            "def": 2,
            "spells": ["Fireball", "Genie", "RockSkin", "Heal"],
        },
    },
    "monsters": {
        "Goblin": {"hp": 2, "atk": 2, "def": 1, "reward": 25},
        "Orc": {"hp": 4, "atk": 3, "def": 2, "reward": 50},
        "Chaos Warrior": {"hp": 8, "atk": 4, "def": 4, "reward": 100},
    },
    "shop": [
        {"name": "Broadsword", "type": "weapon", "atk": 1, "cost": 250},
        {"name": "Plate Mail", "type": "body", "def": 2, "cost": 500},
        {"name": "Shield", "type": "shield", "def": 1, "cost": 150},
        {"name": "Potion of Healing", "type": "item", "cost": 100},
    ],
}


class Character:
    def __init__(self, name, char_class):
        source = (
            GAME_DATA["monsters"]
            if name in GAME_DATA["monsters"]
            else GAME_DATA["heroes"]
        )
        stats = source[char_class]
        self.name, self.char_class = name, char_class
        self.hp = self.max_hp = stats["hp"]
        self.base_atk = stats["atk"]
        self.base_def = stats["def"]
        self.reward = stats.get("reward", 0)
        self.weapon = {"name": "None", "atk": 0}
        self.body_armour = {"name": "None", "def": 0}
        self.shield = {"name": "None", "def": 0}
        self.helmet = {"name": "None", "def": 0}
        self.bracers = {"name": "None", "def": 0}
        self.spells = stats.get("spells", []).copy()
        self.defending = False

    def calculate_atk(self):
        return self.base_atk + self.weapon["atk"]

    def calculate_def(self):
        return (
            self.base_def
            + self.body_armour["def"]
            + self.shield["def"]
            + self.helmet["def"]
            + self.bracers["def"]
            + (1 if self.defending else 0)
        )


# --- 2. SAVE/LOAD LOGIC ---


def save_game(party, gold, floor, inv):
    data = {
        "gold": gold,
        "floor": floor,
        "inventory": inv,
        "heroes": [
            {
                "class": h.char_class,
                "hp": h.hp,
                "max_hp": h.max_hp,
                "wpn": h.weapon,
                "bdy": h.body_armour,
                "shd": h.shield,
                "hlm": h.helmet,
                "brc": h.bracers,
            }
            for h in party
        ],
    }
    with open("heroquest_save.json", "w") as f:
        json.dump(data, f)
    return "DISK ACCESS: SUCCESSFUL"


# --- 3. UI ---


def draw_hud(
    party, gold, inv, floor, room=None, total=None, msg="", foe=None, town=True
):
    os.system("cls" if os.name == "nt" else "clear")
    title = "TOWN HUB" if town else f"DUNGEON F:{floor} R:{room}/{total}"
    print(center(title, Col.HDR + Col.BOLD))
    print(center(f"GOLD: {gold} | POTIONS: {inv.count('Potion of Healing')}", Col.GLD))
    print(Col.EQU + "—" * SCREEN_WIDTH + Col.RST)

    for h in party:
        c = Col.HPG if h.hp > (h.max_hp / 2) else Col.HPR
        print(
            f" {Col.BOLD}{h.name.upper():9}{Col.RST} HP: {c}{h.hp}/{h.max_hp}{Col.RST} | ATK: {Col.HPR}{h.calculate_atk()}{Col.RST} | DEF: {Col.EQU}{h.calculate_def()}{Col.RST}"
        )
        print(
            f" {' ':10} {Col.GLD}WPN: {h.weapon['name']} | BDY: {h.body_armour['name']} | SHD: {h.shield['name']}{Col.RST}"
        )
        if h.spells:
            print(f" {' ':10} {Col.MAG}MAGIC: {', '.join(h.spells)}{Col.RST}")
        print(Col.EQU + "—" * SCREEN_WIDTH + Col.RST)

    if msg:
        print("\n" + center(msg, Col.BOLD))
    if foe:
        print(center(f"VS: {foe.name} (HP: {foe.hp}/{foe.max_hp})", Col.HPR))

    print("\n" + Col.HDR + "=" * SCREEN_WIDTH + Col.RST)
    if town:
        print(center("[C] Continue | [S] Shop | [V] Save | [H] Heal All", Col.BOLD))
    else:
        print(center("[A] Attack | [D] Defend | [M] Magic | [I] Potion", Col.BOLD))
    print(Col.HDR + "=" * SCREEN_WIDTH + Col.RST)


# --- 4. ENGINE ---


def combat(party, gold, inv, floor, room, total):
    m_name = random.choice(list(GAME_DATA["monsters"].keys()))
    foe = Character(m_name, m_name)
    msg = f"A {foe.name} blocks your path!"

    while foe.hp > 0 and any(h.hp > 0 for h in party):
        draw_hud(party, gold, inv, floor, room, total, msg, foe, False)
        for h in party:
            if h.hp <= 0 or foe.hp <= 0:
                continue
            h.defending = False
            act = input(f" [{h.name[:4]}] Command: ").upper()
            if act == "A":
                dmg = max(
                    0,
                    sum(1 for _ in range(h.calculate_atk()) if random.randint(1, 6) > 3)
                    - sum(1 for _ in range(foe.base_def) if random.randint(1, 6) > 4),
                )
                foe.hp -= dmg
                msg = f"{h.name} deals {dmg} DMG."
            elif act == "M" and h.spells:
                spell = h.spells.pop(0)
                foe.hp -= 4
                msg = f"{h.name} cast {spell}!"
            elif act == "D":
                h.defending = True
                msg = f"{h.name} is defending."
            draw_hud(party, gold, inv, floor, room, total, msg, foe, False)
            time.sleep(0.2)

        if foe.hp > 0:
            t = random.choice([h for h in party if h.hp > 0])
            dmg = max(
                0,
                sum(1 for _ in range(foe.base_atk) if random.randint(1, 6) > 3)
                - sum(1 for _ in range(t.calculate_def()) if random.randint(1, 6) > 4),
            )
            t.hp -= dmg
            msg = f"{foe.name} retaliates! {t.name} takes {dmg}."
            time.sleep(0.5)

    if foe.hp <= 0:
        print(center(f"VICTORY! +{foe.reward} Gold.", Col.HPG))
        time.sleep(1)
        return gold + foe.reward, inv
    return gold, inv


def main():
    # Initial Start
    p = [
        Character("Barbarian", "Barbarian"),
        Character("Dwarf", "Dwarf"),
        Character("Elf", "Elf"),
        Character("Wizard", "Wizard"),
    ]
    p[0].weapon = {"name": "Masterwork Blade", "atk": 5}
    g, f, inv = 1226, 13, ["Potion of Healing"] * 2

    while True:
        if not any(h.hp > 0 for h in p):
            print(center("DEFEATED. RESTART? (Y/N)", Col.HPR))
            if input().upper() == "Y":
                main()
            else:
                break

        draw_hud(p, g, inv, f, town=True)
        choice = input(" Town Command: ").upper()

        if choice == "C":
            rooms = 4 + (f // 5)
            for r in range(1, rooms + 1):
                if not any(h.hp > 0 for h in p):
                    break
                g, inv = combat(p, g, inv, f, r, rooms)
                if r < rooms:
                    draw_hud(
                        p, g, inv, f, r, rooms, "Search for Treasure? (Y/N)", town=False
                    )
                    if input().upper() == "Y":
                        res = random.randint(1, 3)
                        if res == 1:
                            p[0].hp -= 2
                            print(center("TRAP! -2 HP", Col.HPR))
                        else:
                            find = random.randint(20, 50)
                            g += find
                            print(center(f"Found {find} Gold!", Col.GLD))
                        time.sleep(1)
            f += 1
            for h in p:
                h.spells = GAME_DATA["heroes"][h.char_class]["spells"].copy()

        elif choice == "V":
            save_game(p, g, f, inv)
            print(center("GAME SAVED TO heroquest_save.json", Col.HPG))
            time.sleep(1)


if __name__ == "__main__":
    main()
