class CombatManager:
    @staticmethod
    def resolve_attack(attacker, defender):
        # 1. Get the dice counts
        atk_dice = attacker.attack
        def_dice = defender.defend

        # 2. Roll the dice
        atk_results = Dice.combat(atk_dice)
        def_results = Dice.combat(def_dice)

        # 3. Determine shield type (The "Referee" rule)
        # Heroes use white, Monsters use black
        hero_classes = ["Barbarian", "Dwarf", "Elf", "Wizard"]
        if defender.char_class in hero_classes:
            shields = def_results["white_shields"]
        else:
            shields = def_results["black_shields"]

        # 4. Final Math
        damage = max(0, atk_results["skulls"] - shields)

        # 5. Apply to the Model
        if damage > 0:
            defender.take_damage(damage)

        # 6. Return a "Report" for the UI to display
        return {
            "skulls": atk_results["skulls"],
            "shields": shields,
            "damage_dealt": damage,
            "target_died": not defender.is_alive,
        }
