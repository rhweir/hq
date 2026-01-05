import random


class Dice:
    def __init__(self, sides, num_dice):
        self.sides = sides
        self.num_dice = num_dice

    def movement(self):
        i = 0
        move = []
        while i < self.num_dice:
            roll = random.randint(1, self.sides)
            i = i + 1
            move.append(roll)
        message = f"Player has rolled a {move[0]} and {move[1]}, a combined total of {sum(move)}."
        return message

    def combat(self):
        i = 0
        result = []
        while i < self.num_dice:
            roll = random.randint(1, self.sides)
            if roll == 1:
                result.append("Monster Sheild")
                i = i + 1
            elif roll > 1 and roll < 5:
                result.append("Skull")
                i = i + 1
            else:
                result.append("Sheild")
                i = i + 1
        return result
