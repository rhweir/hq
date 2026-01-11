import random
from data import GAME_DATA

# ---------------
# 1. Base Classes
# ---------------


class Dice:
    """Method governing attack/defensive rolls"""

    @staticmethod
    def combat(num_dice):
        results = {
            "skulls": 0,
            "white_sh": 0,
            "black_sh": 0,
        }
        for _ in range(num_dice):
            roll = random.randint(1, 6)
            if roll <= 3:  # 50% probability - skulls
                results["skulls"] += 1
            elif roll <= 5:  # 33% probability - white_sh
                results["white_sh"] += 1
            else:  # 16% probability black_sh
                results["black_sh"] += 1
        return results


class Entity:
    """Base class for all Players, Monsters, and NPCs"""

    def __init__(self,
                 char_class,
                 attack,
                 defend,
                 hp,mp
    ):

        self.char_class = char_class
        self.attack = attack
        self.defend = defend
        self.hp = hp
        sel.max_hp = max_hp
        self.is_alive = True

# ---------------
# 2. Sub Classes
# ---------------

class Monster(Entity):
    pass

class Hero(Entity):
    """ Player charachters """

    def __init__(
            self,
            name,
            char_class,
            attack,
            defend,
            hp,
            mp,
            primary_weapon="Unarmed"
    ):
        super().__init__(char_class,0,attack,defend,hp,mp)
        self.name = name
        self.spells = []
        self.gold = 0

class CombatManager:

    @staticmethod
    def resolve_attack(attacker, defender):
        # 1. Get the dice counts
        atk_dice = attacker.attack
        def_dice = defender.defend

        # 2. Roll the dice
        atk_result = Dice.combat(atk_dice)
        def_result = Dice.combat(def_dice)
        

Combat_Manager.calculate_attack_roll("Wizard")""""
