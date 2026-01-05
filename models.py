import random
import data
from dice import Dice


class Entity:
    """Base class for all PCs & NPCs"""

    def __init__(self, char_class, movement, attack, defend, hp, mp, x=0, y=0):
        self.char_class = char_class
        self.base_movement = movement
        self.base_attack = attack
        self.base_defend = defend
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
