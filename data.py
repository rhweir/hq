# ==========================================
# HEROQUEST UK EDITION DATA
# ==========================================

# Weapon dictionary (UK Prices and Stats)
# Note: In the UK, weapons like the Battle Axe and Staff
# prevent the use of a Shield (Two-handed).
import csv


def load_csv_data(filepath):
    """Parses CSV into a list of dictionaries"""
    data_list = []
    try:
        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data_list.append(dict(row))
    except FileNotFoundError:
        print(f"Error: {filepath} not found. Library will be empty.")
    except Exception as e:
        print(f"An error occurred loading {filepath}: {e}")
    return data_list


# Load the cards into 'library' variables
spell_library = load_csv_data("spells.csv")
treasure_deck = load_csv_data("treasure.csv")

print(spell_library)

weapons = {
    "Dagger": {
        "cost": 25,
        "attack_bonus": 1,
        "melee": True,
        "ranged": False,
        "diagonal": False,
        "thrown": True,
        "two_handed": False,
        "wizard_ok": True,
        "stackable": True,
        "min_range": 0,
    },
    "Staff": {
        "cost": 100,
        "attack_bonus": 2,
        "melee": True,
        "ranged": False,
        "diagonal": True,
        "thrown": False,
        "two_handed": True,
        "wizard_ok": True,
        "stackable": False,
        "min_range": 0,
    },
    "Shortsword": {
        "cost": 150,
        "attack_bonus": 2,
        "melee": True,
        "ranged": False,
        "diagonal": False,
        "thrown": False,
        "two_handed": False,
        "wizard_ok": False,
        "stackable": False,
        "min_range": 0,
    },
    "Hand Axe": {
        "cost": 150,
        "attack_bonus": 2,
        "melee": True,
        "ranged": False,
        "diagonal": False,
        "thrown": True,
        "two_handed": False,
        "wizard_ok": False,
        "stackable": True,
        "min_range": 0,
    },
    "Broadsword": {
        "cost": 250,
        "attack_bonus": 3,
        "melee": True,
        "ranged": False,
        "diagonal": False,
        "thrown": False,
        "two_handed": False,
        "wizard_ok": False,
        "stackable": False,
        "min_range": 0,
    },
    "Longsword": {
        "cost": 350,
        "attack_bonus": 3,
        "melee": True,
        "ranged": False,
        "diagonal": True,
        "thrown": False,
        "two_handed": False,
        "wizard_ok": False,
        "stackable": False,
        "min_range": 0,
    },
    "Crossbow": {
        "cost": 350,
        "attack_bonus": 3,
        "melee": False,
        "ranged": True,
        "diagonal": False,
        "thrown": False,
        "two_handed": False,
        "wizard_ok": False,
        "stackable": False,
        "min_range": 2,
    },
    "Battle Axe": {
        "cost": 450,
        "attack_bonus": 4,
        "melee": True,
        "ranged": False,
        "diagonal": False,
        "thrown": False,
        "two_handed": True,
        "wizard_ok": False,
        "stackable": False,
        "min_range": 0,
    },
    "Unarmed": {
        "cost": 0,
        "attack_bonus": 1,
        "melee": True,
        "ranged": False,
        "diagonal": False,
        "thrown": False,
        "two_handed": False,
        "wizard_ok": True,
        "stackable": False,
        "min_range": 0,
    },
}

# Armour Dictionary (UK Prices)
armour = {
    "Helmet": {
        "cost": 120,  # UK Price
        "defence_bonus": 1,
        "wizard_ok": False,
        "is_body_armour": False,
        "is_off_hand": False,
        "move_penalty": 0,
        "slot": "head",
    },
    "Shield": {
        "cost": 100,  # UK Price
        "defence_bonus": 1,
        "wizard_ok": False,
        "is_body_armour": False,
        "is_off_hand": True,
        "move_penalty": 0,
        "slot": "off_hand",
    },
    "Chain Mail": {
        "cost": 450,  # UK Price
        "defence_bonus": 1,
        "wizard_ok": False,
        "is_body_armour": True,
        "is_off_hand": False,
        "move_penalty": 0,
        "slot": "body",
    },
    "Plate Mail": {
        "cost": 500,  # UK Price (Armor)
        "defence_bonus": 2,
        "wizard_ok": False,
        "is_body_armour": True,
        "is_off_hand": False,
        "move_penalty": 1,  # Often played as half-movement roll in UK
        "slot": "body",
    },
    "Empty": {
        "cost": 0,
        "defence_bonus": 0,
        "wizard_ok": True,
        "is_body_armour": False,
        "is_off_hand": False,
        "move_penalty": 0,
        "slot": None,
    },
}

# Hero Dictionary (UK Starting Equipment)
hero_templates = {
    "Barbarian": {
        "movement": 0,
        "attack": 0,
        "defend": 2,
        "hp": 8,
        "mp": 2,
        "primary_weapon": "Broadsword",
    },
    "Dwarf": {
        "movement": 0,
        "attack": 0,
        "defend": 2,
        "hp": 7,
        "mp": 3,
        "primary_weapon": "Shortsword",
    },
    "Elf": {
        "movement": 0,
        "attack": 0,
        "defend": 2,
        "hp": 6,
        "mp": 4,
        "primary_weapon": "Shortsword",
    },
    "Wizard": {
        "movement": 0,
        "attack": 0,
        "defend": 2,  # Note: In UK manual Wizard defends with 2, but often played with 1
        "hp": 4,
        "mp": 6,
        "primary_weapon": "Dagger",
    },
}

# Monster Dictionary (Strict UK Stats - All 1 HP)
monster_templates = {
    "Goblin": {
        "movement": 10,
        "attack": 2,
        "defend": 1,
        "hp": 1,
        "mp": 1,
    },
    "Skeleton": {
        "movement": 6,
        "attack": 2,
        "defend": 2,
        "hp": 1,
        "mp": 0,
    },
    "Zombie": {
        "movement": 5,
        "attack": 2,
        "defend": 3,
        "hp": 1,
        "mp": 0,
    },
    "Orc": {
        "movement": 8,
        "attack": 3,
        "defend": 2,
        "hp": 1,
        "mp": 2,
    },
    "Fimir": {
        "movement": 6,
        "attack": 3,
        "defend": 3,
        "hp": 1,
        "mp": 3,
    },
    "Mummy": {
        "movement": 4,
        "attack": 3,
        "defend": 4,
        "hp": 1,
        "mp": 0,
    },
    "Chaos Warrior": {
        "movement": 6,
        "attack": 4,
        "defend": 4,
        "hp": 1,
        "mp": 3,
    },
    "Gargoyle": {
        "movement": 6,
        "attack": 4,
        "defend": 5,
        "hp": 1,
        "mp": 4,
    },
}
