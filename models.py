import data


class Entity:
    """Base class for all creatures and heroes"""

    def __init__(
        self, alignment, char_class, movement, base_attack, base_defend, hp, mp, weapon
    ):

        self.alignment = alignment
        self.char_class = char_class
        if self.alignment == "Lawful":
            self.movement = 0
        else:
            self.movement = movement

        # Equipment Objects
        self.weapon = data.weapons.get(weapon, data.weapons["Unarmed"])
        self.head = data.armour["Empty"]
        self.body = data.armour["Empty"]
        self.off_hand = data.armour["Empty"]
        self.arm = data.armour["Empty"]

        # Base Stats (Strenght/Toughness)
        self.base_attack = base_attack
        self.base_defend = base_defend

        # Current Status
        self.hp = hp
        self.mp = mp

    def get_total_attack(self):

        if self.alignment == "Lawful":
            total_attack = self.base_attack + self.weapon["attack_bonus"]
            return total_attack
        else:
            return self.base_attack

    def get_total_defend(self):

        if self.alignment == "Lawful":
            bonus = (
                self.head["defence_bonus"]
                + self.body["defence_bonus"]
                + self.off_hand["defence_bonus"]
                + self.arm["defence_bonus"]
            )
            return self.base_defend + bonus
        else:
            return self.base_defend

    def roll_for_movement(self):
        """Called at the start of the player turn"""
        if self.alignment == "Lawful":
            import random

            # Roll dice
            roll = random.randint(1, 6) + random.randint(1, 6)
            self.movement = roll

            # Calculate armour penalties
            penalty = (
                self.head.get("move_penalty", 0)
                + self.body.get("move_penalty", 0)
                + self.off_hand.get("move_penalty", 0)
                + self.arm.get("move_penalty", 0)
            )

            # Set remaining movement (min 1)
            self.movement_remaining = max(1, roll - penalty)

        else:
            # monsters use hardcoded values
            self.movement_remaining = self.movement

    def step(self):
        """Reduces movement by 1. Call this every time an entity moves one tile"""
        if self.movement_remaining > 0:
            self.movement_remaining -= 1
            return True  # move succesful
        return False  # no movement left


monster_01 = Entity("Chaotic", "Zombie", 5, 2, 3, 1, 0, None)
monster_02 = Entity("Chaotic", "Mummy", 4, 3, 4, 2, 0, None)
monster_03 = Entity("Chaotic", "Gargoyle", 6, 4, 5, 3, 0, None)
monster_04 = Entity("Chaotic", "Orc", 8, 3, 2, 1, 2, None)
monster_05 = Entity("Chaotic", "Skeleton", 6, 2, 2, 1, 0, None)
monster_06 = Entity("Chaotic", "Goblin", 10, 2, 1, 1, 1, None)
monster_07 = Entity("Chaotic", "Chaos Warrior", 7, 4, 4, 3, 3, None)
monster_08 = Entity("Chaotic", "Fimir", 6, 3, 3, 2, 3, None)
monster_09 = Entity("Chaotic", "Chaos Warlock", 8, 3, 3, 1, 4, None)

player_01 = Entity("Lawful", "Barbarian", 0, 0, 2, 8, 2, "Broadsword")
player_02 = Entity("Lawful", "Dwarf", 0, 0, 2, 7, 3, "Shortsword")
player_03 = Entity("Lawful", "Elf", 0, 0, 2, 6, 4, "Shortsword")
player_04 = Entity("Lawful", "Wizard", 0, 0, 2, 4, 6, "Dagger")
