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

    def calculate_defence_dice(self):
        """Adds up the base defence and armour bonuses"""

        # 1. Start with the base stat saved in Entity
        total_dice = self.base_defend

        # 2. Add equipment bonuses
        total_dice += self.off_hand.get("defence_bonus", 0)
        total_dice += self.head.get("defence_bonus", 0)
        total_dice += self.body.get("defence_bonus", 0)
        total_dice += self.arm.get("defence_bonus", 0)

        return total_dice

    def calculate_attack_dice(self):
        """Adds up base attack and weapon bonus"""

        # 1. Start with the base attack saved in Entity
        total_dice = self.base_attack

        # 2. Add weapon bonus
        total_dice += self.primary_weapon.get("attack_bonus", 0)

        return total_dice


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
    print("--- ⚔️  RPG SYSTEM TEST ⚔️  ---")

    # 1. Test Hero Spawning with a Template Weapon
    conan = spawn_hero("Conan", "Barbarian", x=1, y=1)
    if conan:
        print(f"\nHero: {conan.name} the {conan.char_class}")
        print(
            f"Weapon: {conan.primary_weapon.get('cost') > 0 and 'Broadsword' or 'None'}"
        )
        # This uses your new method!
        print(f"Total Attack Dice: {conan.calculate_attack_dice()}")
        print(f"Total Defense Dice: {conan.calculate_defence_dice()}")

    # 2. Test Unarmed Logic (Wizard)
    merlin = spawn_hero("Merlin", "Wizard")
    if merlin:
        # We manually set him to Unarmed to be sure
        merlin.primary_weapon = data.weapons["Unarmed"]
        print(f"\nHero: {merlin.name} the {merlin.char_class}")
        print(f"Weapon: Unarmed")
        # Base Attack (0) + Unarmed Bonus (1) = 1
        print(f"Total Attack Dice: {merlin.calculate_attack_dice()}")

    # 3. Test Monster Spawning
    grunt = spawn_monster("Orc", x=5, y=5)
    if grunt:
        print(f"\nMonster: {grunt.char_class}")
        print(f"Position: ({grunt.x}, {grunt.y})")
        print(f"Base Attack: {grunt.base_attack}")
        print(f"Base Defense: {grunt.base_defend}")

    # 4. Test Equipment Change
    print(f"\n--- 🛡️  EQUIPMENT TEST ---")
    print(f"Conan's Defense before Shield: {conan.calculate_defence_dice()}")
    conan.off_hand = data.armour["Shield"]
    print(f"Conan's Defense after Shield: {conan.calculate_defence_dice()}")
