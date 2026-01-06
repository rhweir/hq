import json


def load_game_data(filepath="gamedata.json"):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return {}


# Load global libraries
GAME_DATA = load_game_data()
