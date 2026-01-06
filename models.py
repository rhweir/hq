import random
import json


def load_game_data(filepath="gamedata.json"):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return {}


# Load global libraries
GAME_DATA = load_game_data()

# ==========================================
# 1. BASE CLASSES
# ==========================================


class Dice:

    @staticmethod
    def combat(num_dice):
        results = {"skulls": 0, "white_shields": 0, "black_shields": 0}
        for _ in range(num_dice):
            roll = random.randint(1, 6)
            if roll <= 3:  # 1, 2, 3 (50% Skull)
                results["skulls"] += 1
            elif roll <= 5:  # 4, 5 (33% White Shield)
                results["white_shields"] += 1
            else:  # 6 (16% Black Shield)
                results["black_shields"] += 1
        return results


class Entity:
    """Base class for all PCs & NPCs"""

    def __init__(self, char_class, movement, attack, defend, hp, mp, x=0, y=0):
        self.char_class = char_class
        self.base_movement = movement
        self.base_attack = attack
        self.base_defend = defend
        self.hp = hp
        self.mp = mp
        self.x = x
        self.y = y
        self.defence_key = "white_shields"  # Default

    def calculate_attack_dice(self):
        return self.base_attack

    def calculate_defence_dice(self):
        return self.base_defend

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        print(f"{self.char_class} takes {amount} damage! HP is now {self.hp}")
        if self.hp == 0:
            print(f"!!! {self.char_class} has been slain!!!")
        return self.hp > 0

    def perform_attack(self, target):
        attack_dice = self.calculate_attack_dice()
        attack_results = Dice.combat(attack_dice)
        skulls = attack_results["skulls"]

        defend_dice = target.calculate_defence_dice()
        defend_results = Dice.combat(defend_dice)
        blocks = defend_results.get(target.defence_key, 0)

        damage = max(0, skulls - blocks)
        print(f"\n--- Combat: {self.char_class} vs {target.char_class} ---")
        print(
            f"Attacker: {skulls} Skulls | Defender: {blocks} {target.defence_key.replace('-',' ').title()}"
        )

        if damage > 0:
            target.take_damage(damage)
        else:
            print("The attack was completely blocked!")

    def is_adjacent(self, target):
        dx, dy = abs(self.x - target.x), abs(self.y - target.y)
        weapon = getattr(self, "primary_weapon", {})
        if weapon.get("diagonal", False):
            return max(dx, dy) == 1
        return (dx + dy) == 1


# ==========================================
# 2. SUB-CLASSES
# ==========================================


class Monster(Entity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.defence_key = "black_shields"


class Hero(Entity):
    """Hero with equipment and rolling logic"""

    def __init__(
        self,
        name,
        char_class,
        attack,
        defend,
        hp,
        mp,
        x=0,
        y=0,
        primary_weapon="Unarmed",
    ):
        super().__init__(char_class, 0, attack, defend, hp, mp, x, y)
        self.name = name:
        self.defence_key = "white_shields"

        # Pull weapon/armour data from the JSON library
        weapon_lib = GAME_DATA.get("weapons",{})
        armour_lib = GAME_DATA.get("armour",{})
        
        self.primary_weapon = weapon_lib.get(primary_weapon, weapon_lib.get("Unarmed", {}))
        self.slots = {
            "head": armour_lib.get("Empty"),
            "body": armour_lib.get("Empty"),
            "off_hand": armour_lib.get("Empty")
        }

    def roll_for_movement(self):
        """Calculates player movement (2d6) minus armour penalties"""
        roll = random.randint(1, 6) + random.randint(1, 6)

        # Plate Mail causes movement penalty
        penalty = sum(item.get("move_penalty",0) for item in self.slots.values() if item)

        self.movement_remaining = max(1, roll - penalty)
        print(f"{self_name} rolled a {roll} for movement (Penalty: {penalty}). Total {self.movement_remaining}")
        return self.movement_remaining

    def calculate_attack_dice(self):
        return self.base_attack + self.primary_weapon.get("attack_bonus", 0)

    def calculate_defence_dice(self):
        bonus = sum(item.get("defence_bonus", 0) for item in self.slots.values() if item)
        # Check for two handed weapon blocking shield use 
        if self.primary_weapon.get("two_handed", False):
            off_hand = self.slots.get("off_hand", {})
            if off_hand and off_hand.get("slot") == "off_hand":
                bonus -= off_hand.get("defence_bonus",0)
            return self.base_defend + bonus


# ==========================================
# 3. SPAWNING FUNCTIONS (THE BRIDGE)
# ==========================================


def spawn_hero(hero_name, class_type, x=0, y=0):
    template = data.hero_templates.get(class_type)
    if not template:
        print(f"Error: Class '{class_type}' not found.")
        return None

    weapon_name = template["primary_weapon"]
    weapon_info = data.weapons.get(weapon_name, data.weapons["Unarmed"])

    # Wizard weapon check
    if class_type == "Wizard" and not weapon_info.get("wizard_ok", False):
        print(
            f"Illegal Equipment: {class_type} cannot use {weapon_name}. Equipping Dagger instead."
        )
        weapon_name = "Dagger"

    # Create the hero
    hero = Hero(
        name=hero_name,
        char_class=class_type,
        attack=template["attack"],
        defend=template["defend"],
        hp=template["hp"],
        mp=template["mp"],
        x=x,
        y=y,
        primary_weapon=weapon_name,
    )

    # Wizard armour check
    if class_type == "Wizard":
        for slot in hero.slots:
            if not hero.slots[slot].get("wizard_ok", True):
                print(f"Illegal Armour: {class_type} cannot use {slot} item. Removing.")
                hero.slots[slot] = data.armour["Empty"]

    return hero


def spawn_monster(monster_type, x=0, y=0):
    template = data.monster_templates.get(monster_type)
    if not template:
        print(f"Error: Monster '{monster_type}' not found.")
        return None

    return Monster(
        char_class=monster_type,
        movement=template["movement"],
        attack=template["attack"],
        defend=template["defend"],
        hp=template["hp"],
        mp=template["mp"],
        x=x,
        y=y,
    )


# ==========================================
# 4. TEST EXECUTION
# ==========================================
if __name__ == "__main__":
    # Test spawns
    hero = spawn_hero("Conan", "Barbarian")
    orc = spawn_monster("Orc")

    if hero and orc:
        print(f"TEST: {hero.name} has {hero.calculate_attack_dice()} attack dice.")
        print(f"TEST: {orc.char_class} has {orc.calculate_attack_dice()} attack dice.")

    if hero and orc:
        print(f"A wild {orc.char_class} appears!")

        # Keep fighting as long as both have HP
        while hero.hp > 0 and orc.hp > 0:
            hero.perform_attack(orc)

            if orc.hp > 0:
                orc.perform_attack(hero)

            print("-" * 25)

        if hero.hp > 0:
            print(f"VICTORY: {hero.name} survived with {hero.hp} HP!")
        else:
            print("DEFEAT: The dungeon has claimed another soul.")
