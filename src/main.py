from services import SpeedrunService


def main():
    speedrun_service = SpeedrunService()
    game = speedrun_service.get_game()
    print(game)


if __name__ == "__main__":
    main()
