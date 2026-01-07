import random
from data import GAME_DATA

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
        self.movement_remaining = 0
        self.defence_key = "white_shields"

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
        if not self.is_adjacent(target):
            print(f"!!! {target.char_class} is too far away to attack! !!!")
            return

        attack_dice = self.calculate_attack_dice()
        attack_results = Dice.combat(attack_dice)
        skulls = attack_results["skulls"]

        defend_dice = target.calculate_defence_dice()
        defend_results = Dice.combat(defend_dice)
        blocks = defend_results.get(target.defence_key, 0)

        damage = max(0, skulls - blocks)
        print(f"\n--- Combat: {self.char_class} vs {target.char_class} ---")
        print(
            f"Attacker: {skulls} Skulls | Defender: {blocks} {target.defence_key.replace('_',' ').title()}"
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
        self.name = name
        self.defence_key = "white_shields"
        self.spells = []

        # Pull weapon/armour data from the JSON library
        weapon_lib = GAME_DATA.get("weapons", {})
        armour_lib = GAME_DATA.get("armour", {})

        null_item = {"cost": 0, "defence_bonus": 0, "attack_bonus": 0, "slot": None}

        self.primary_weapon = weapon_lib.get(
            primary_weapon, weapon_lib.get("Unarmed", null_item)
        )
        self.slots = {
            "head": armour_lib.get("Empty", null_item),
            "body": armour_lib.get("Empty", null_item),
            "off_hand": armour_lib.get("Empty", null_item),
        }

    def cast_spell(self, spell_name, target=None):
        """Spells discarded after use."""
        spell = next((s for s in self.spells if s["name"] == spell_name), None)

        if spell:
            print(f"{self.name} casts {spell['name']}! ***")
            # Logic for spell effects (Damage/Healing) to go here later
            self.spells.remove(spell)
            return True
        else:
            print(f"ERROR: {self.name} does not have the spell '{spell_name}'!")
            return False

    def roll_for_movement(self):
        """Calculates player movement (2d6) minus armour penalties"""
        roll = random.randint(1, 6) + random.randint(1, 6)

        # Plate Mail causes movement penalty
        penalty = sum(
            item.get("move_penalty", 0) for item in self.slots.values() if item
        )

        self.movement_remaining = max(1, roll - penalty)
        print(
            f"{self.name} rolled a {roll} for movement (Penalty: {penalty}). Total {self.movement_remaining}"
        )
        return self.movement_remaining

    def calculate_attack_dice(self):
        return self.base_attack + self.primary_weapon.get("attack_bonus", 0)

    def calculate_defence_dice(self):
        bonus = sum(
            item.get("defence_bonus", 0) for item in self.slots.values() if item
        )
        # Check for two handed weapon blocking shield use
        if self.primary_weapon.get("two_handed", False):
            off_hand = self.slots.get("off_hand") or {}
            if off_hand.get("slot") == "off_hand":
                bonus -= off_hand.get("defence_bonus", 0)
        return self.base_defend + bonus


# ==========================================
# 3. SPAWNING FUNCTIONS
# ==========================================


def spawn_hero(hero_name, class_type, x=0, y=0, chosen_spells=None):
    hero_lib = GAME_DATA.get("heroes", {})
    template = hero_lib.get(class_type)
    if not template:
        print(f"CRITICAL ERROR: Hero class '{class_type}' not found in data!")
        return Hero(hero_name, "Adventurer", 1, 2, 4, 2, x, y)

    hero = Hero(
        name=hero_name,
        char_class=class_type,
        attack=template.get("attack", 1),
        defend=template.get("defend", 2),
        hp=template.get("hp", 4),
        mp=template.get("mp", 2),
        x=x,
        y=y,
        primary_weapon=template.get("primary_weapon", "Unarmed"),
    )

    if class_type == "Wizard":
        for slot, item in hero.slots.items():
            if not item.get("wizard_ok", True):
                print(f"Illegal Armour: Wizard cannot wear {slot}. Removing.")
                hero.slots[slot] = GAME_DATA["armour"]["Empty"]

    if template.get("is_spellcaster") and chosen_spells:
        spell_lib = GAME_DATA.get("spells", {})
        for element in chosen_spells:
            element_spells = spell_lib.get(element, [])
            hero.spells.extend(element_spells)
            print(f"Assigning {element} spells to {hero.name}...")

    return hero


def spawn_monster(monster_type, x=0, y=0):
    monster_lib = GAME_DATA.get("monsters", {})
    template = monster_lib.get(monster_type)
    if not template:
        print(f"CRITICAL ERROR: Monster type '{monster_type}' not found in data!")
        return None

    return Monster(
        char_class=monster_type,
        movement=template.get("movement", 6),
        attack=template.get("attack", 2),
        defend=template.get("defend", 2),
        hp=template.get("hp", 1),
        mp=template.get("mp", 0),
        x=x,
        y=y,
    )
