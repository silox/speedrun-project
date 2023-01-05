import json
from services import SpeedrunService


def main():
    speedrun_service = SpeedrunService()
    statistics = speedrun_service.get_statistics()
    with open("game_data.json", "w") as f:
        json.dump(statistics, f, indent=2)


if __name__ == "__main__":
    main()
