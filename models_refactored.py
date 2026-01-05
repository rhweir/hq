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
