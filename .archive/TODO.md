⚔️ HeroQuest Combat Logic To-Do List
1. Dice Engine (dice.py)

    [ ] Create the Dice Class/Functions: Build a system that simulates the special six-sided HeroQuest combat dice.

    [ ] Define Symbol Logic:

        Skulls: (3 in 6 chance) — Represents a successful hit.

        White Shields: (2 in 6 chance) — Represents a Hero (Lawful) blocking a hit.

        Black Shields: (1 in 6 chance) — Represents a Monster (Chaotic) blocking a hit.

    [ ] Roll Results: Create a function that takes the number of dice (from get_total_attack or get_total_defend) and returns the count of specific symbols rolled.

2. Entity Class Updates (models.py)

    [ ] Damage Application: Add a take_damage(self, amount) method to subtract points from self.hp.

    [ ] Death Check: Add an is_alive(self) method that returns False if self.hp <= 0.

    [ ] Attack Method: Create an attack_target(self, target) method that:

        Calls self.get_total_attack() to get the number of attack dice.

        Calls the target's target.get_total_defend() to get defense dice.

        Calculates the "Net Damage" (Skulls rolled minus the correct shields rolled).

3. Combat Rules & Edge Cases

    [ ] Alignment Shield Check: Ensure the logic uses White Shields for "Lawful" defenders and Black Shields for "Chaotic" defenders.

    [ ] Minimum Damage: Ensure damage cannot be negative (if a defender rolls more shields than the attacker rolls skulls, damage is 0, not a health increase).

4. Integration Testing (Console Phase)

    [ ] Simulated Duel: Write a temporary script to make player_01 (Barbarian) attack monster_01 (Zombie) in a loop until one is defeated.

    [ ] Print Feedback: Print the results of each roll to the console to verify that the weapon["attack_bonus"] and hardcoded monster stats are being applied correctly.
