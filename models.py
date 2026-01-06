import random
import data

# ==========================================
# 1. BASE CLASSES
# ==========================================


class Dice:

    @staticmethod
    def combat(num_dice):
        results = {"skulls": 0, "white_shields": 0, "black_shields": 0}
        for _ in range(num_dice):
            roll = random.randint(1, 6)
            if roll <= 3:  # 1, 2, 3
                results["skulls"] += 1
            elif roll <= 5:  # 4, 5
                results["white_shields"] += 1
            else:
                results["black_shields"] += 1
        return results


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

        # Position variables
        self.x = x
        self.y = y

    def calculate_attack_dice(self):
        return self.base_attack

    def calculate_defence_dice(self):
        return self.base_defend

    def take_damage(self, amount):
        """Reduces HP and returns True if alive, False if dead"""
        self.hp -= amount

        # Prevent HP from being negative
        if self.hp < 0:
            self.hp = 0

        print(f"{self.char_class} takes {amount} damage! HP is now {self.hp}")

        if self.hp == 0:
            print(f"!!! {self.char_class} has been slain !!!")

        return self.hp > 0

    def perform_attack(self, target):
        """Rolls attack v target defence"""

        # 1. Attacker rolls for skulls
        attack_dice = self.calculate_attack_dice()
        attack_results = Dice.combat(attack_dice)
        skulls = attack_results["skulls"]

        # 2. Target rolls for shields
        defend_dice = target.calculate_defence_dice()
        defend_results = Dice.combat(defend_dice)

        # 3. Choose the correct shield (White for heros, black for monsters)
        blocks = defend_results.get(target.defence_key, 0)
        shield_name = target.defence_key.replace("_", " ").title()

        # 4. Final Result
        damage = max(0, skulls - blocks)

        print(f"\n--- Combat: {self.char_class} vs {target.char_class} ---")
        print(f"Attacker rolls: {skulls} Skulls")
        print(f"Defender rolls: {blocks} {shield_name}")

        if damage > 0:
            target.take_damage(damage)
        else:
            print("The attack was completely blocked!")


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
        head="Empty",
        body="Empty",
        off_hand="Empty",
        arm="Empty",
    ):

        # Hero movement is always 0 until they roll
        super().__init__(char_class, 0, attack, defend, hp, mp, x, y)

        self.name = name
        self.defence_key = "white_shields"

        # Equipment Lookups
        self.primary_weapon = data.weapons.get(primary_weapon, data.weapons["Unarmed"])

        self.slots = {
            "head": data.armour.get(head, data.armour["Empty"]),
            "body": data.armour.get(body, data.armour["Empty"]),
            "off_hand": data.armour.get(off_hand, data.armour["Empty"]),
            "arm": data.armour.get(arm, data.armour["Empty"]),
        }

    def roll_for_movement(self):
        """Calculates player movement (2d6) minus armour penalties"""
        roll = random.randint(1, 6) + random.randint(1, 6)

        penalty = sum(item.get("move_penalty", 0) for item in self.slots.values())

        self.movement_remaining = max(1, roll - penalty)
        return self.movement_remaining

    def calculate_attack_dice(self):
        """Combines base attack and weapon bonus"""
        return self.base_attack + self.primary_weapon.get("attack_bonus", 0)

    def calculate_defence_dice(self):
        """Adds up base defence and all armour bonuses"""
        bonus = sum(item.get("defence_bonus", 0) for item in self.slots.values())
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
