import os


class Map:
    def __init__(self, width=26, height=19):
        """
        Initializes the board dimensions.
        Standard HeroQuest (UK Edition) is 26x19.
        """
        self.width = width
        self.height = height

    def render(self, heroes, monsters):
        """
        Clears the terminal and draws the grid, heroes, and monsters.
        """
        # Clear the terminal for a TUI feel
        # 'cls' for Windows, 'clear' for POSIX (Linux/Mac)
        os.system("cls" if os.name == "nt" else "clear")

        # 1. Print Column Headers (00, 01, 02...)
        header = "   " + "".join([f"{x:02} " for x in range(self.width)])
        print(header)

        # 2. Iterate through each row (y-axis)
        for y in range(self.height):
            # Print Row Header (00, 01, 02...)
            line = f"{y:02} "

            # 3. Iterate through each column (x-axis)
            for x in range(self.width):
                # Check if a hero is standing at this coordinate
                occupant = next((h for h in heroes if h.x == x and h.y == y), None)

                # If no hero, check if a monster is at this coordinate
                if not occupant:
                    occupant = next(
                        (m for m in monsters if m.x == x and m.y == y), None
                    )

                if occupant:
                    # Draw the first letter of the character class (e.g., 'W', 'G')
                    line += f" {occupant.char_class[0]} "
                else:
                    # Draw an empty floor tile
                    line += " . "

            print(line)
