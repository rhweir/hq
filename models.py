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

        return self.hp > 0

    def perform_attack(self, target):
        """Rolls attack v target defence"""

        # 1. Attacker rolls for skulls
        attack_dice = self.calculate_attack_dice()
        attack_results = Dice.roll_combat_dice(attack_dice)
        skulls = attack_results["skulls"]


# ==========================================
# 2. SUB-CLASSES
# ==========================================


class Monster(Entity):
    """Standard monster, inherits from Entity"""

    pass  # do nothing


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
        off_hand="Empty",
        arm="Empty",
        head="Empty",
        body="Empty",
    ):

        # Hero movement is always 0 until they roll
        super().__init__(char_class, 0, attack, defend, hp, mp, x, y)

        self.name = name

        # Equipment Lookups
        self.primary_weapon = data.weapons.get(primary_weapon, data.weapons["Unarmed"])
        self.off_hand = data.armour.get(off_hand, data.armour["Empty"])
        self.arm = data.armour.get(arm, data.armour["Empty"])
        self.head = data.armour.get(head, data.armour["Empty"])
        self.body = data.armour.get(body, data.armour["Empty"])

    def roll_for_movement(self):
        """Calculates player movement (2d6) minus armour penalties"""
        roll = random.randint(1, 6) + random.randint(1, 6)

        penalty = (
            self.off_hand.get("move_penalty", 0)
            + self.arm.get("move_penalty", 0)
            + self.head.get("move_penalty", 0)
            + self.body.get("move_penalty", 0)
        )

        self.movement_remaining = max(1, roll - penalty)
        return self.movement_remaining

    def calculate_attack_dice(self):
        """Combines base attack and weapon bonus"""
        return self.base_attack + self.primary_weapon.get("attack_bonus", 0)

    def calculate_defence_dice(self):
        """Adds up base defence and all armour bonuses"""
        total_dice = self.base_defend
        total_dice += self.off_hand.get("defence_bonus", 0)
        total_dice += self.head.get("defence_bonus", 0)
        total_dice += self.body.get("defence_bonus", 0)
        total_dice += self.arm.get("defence_bonus", 0)
        return total_dice


# ==========================================
# 3. SPAWNING FUNCTIONS (THE BRIDGE)
# ==========================================


def spawn_hero(hero_name, class_type, x=0, y=0):
    template = data.hero_templates.get(class_type)
    if not template:
        print(f"Error: Class '{class_type}' not found.")
        return None

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
