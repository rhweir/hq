import random
import data
from dice import Dice


class Entity:
    """Base class for all PCs & NPCs"""

    def __init__(self, char_class, movement, attack, defend, hp, mp, x=0, y=0):
        self.char_class = char_class

        # Permanent stats
        self.base_movement = movement
        self.base_attack = attack
        self.base_defend = defend

        # Current stats
        self.hp = hp
        self.mp = mp
        self.movement_remaining = 0

        # position variables
        self.x = x
        self.y = y


class Monster(Entity):
    """Standard monster, inherits everything from the Entity class"""

    pass  # do nothing else


class Boss(Entity):
    """Monster with specific elements"""

    def __init__(self, name, char_class, movement, attack, defend, hp, mp, x=0, y=0):
        super().__init__(char_class, movement, attack, defend, hp, mp, x, y)
        self.name = name


class Hero(Entity):
    """Hero with specific elements"""

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
        off_hand="Empty",
        arm="Empty",
        head="Empty",
        body="Empty",
    ):
        super().__init__(char_class, 0, attack, defend, hp, mp, x, y)

        self.name = name
        self.primary_weapon = data.weapons.get(primary_weapon, data.weapons["Unarmed"])
        self.off_hand = data.armour.get(off_hand, data.armour["Empty"])
        self.arm = data.armour.get(arm, data.armour["Empty"])
        self.head = data.armour.get(head, data.armour["Empty"])
        self.body = data.armour.get(body, data.armour["Empty"])

    def roll_for_movement(self):
        """Calculates player movement minus armour penalties"""
        # Roll 2d6
        roll = random.randint(1, 6) + random.randint(1, 6)

        # Calculalte armour penalties
        penalty = (
            self.off_hand.get("move_penalty", 0)
            + self.arm.get("move_penalty", 0)
            + self.head.get("move_penalty", 0)
            + self.body.get("move_penalty", 0)
        )

        # Set remaining movement (min 1)
        self.movement_remaining = max(1, roll - penalty)
        return self.movement_remaining


def spawn_hero(hero_name, class_type, x=0, y=0):
    # 1. Lookup the template in data.py
    template = data.hero_templates.get(class_type)

    if template is None:
        print(f"Error: Class '{class_type}' not found in hero template")
        return None

    # 2. Extract the stats from the template
    return Hero(
        name=hero_name,
        char_class=class_type,
        attack=template["attack"],
        defend=template["defend"],
        hp=template["hp"],
        mp=template["mp"],
        x=x,
        y=y,
        primary_weapon=template["primary_weapon"],
    )


def spawn_monster(monster_type, x=0, y=0):
    template = data.monster_templates.get(monster_type)

    if template is None:
        print(f"Error: Monster '{monster_type}' not found")
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


if __name__ == "__main__":
    # 1. Use the bridge to spawn a Barbarian
    # The Barbarian template in data.py has "attack": 0
    my_hero = spawn_hero("Conan", "Barbarian", x=1, y=1)

    if my_hero:
        print("--- SPAWN TEST ---")
        print(f"Name: {my_hero.name}")
        print(f"Class: {my_hero.char_class}")

        # 2. Check the "Hand-off"
        # Even though we passed it in as 'attack', it's now 'base_attack'
        print(f"Base Attack Stat: {my_hero.base_attack}")

        # 3. Check the Weapon lookup
        # The bridge took the string "Broadsword" and turned it into a dictionary
        weapon_bonus = my_hero.primary_weapon["attack_bonus"]
        print(f"Weapon Bonus: {weapon_bonus}")

        # 4. Show the math for the future
        total_dice = my_hero.base_attack + weapon_bonus
        print(f"Total Attack Dice: {total_dice}")
