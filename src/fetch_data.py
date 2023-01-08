import json
from os import path

from tqdm import tqdm

from services.speedrun_service import SpeedrunService
from services.json_dumper import GameJSONDumper, RunJSONDumper


def fetch_games():
    if path.exists("data/games.json"):
        print("Games already fetched. Skipping...")
        return

    speedrun_service = SpeedrunService()
    games = speedrun_service.get_games_with_jp_region()
    GameJSONDumper("games.json").dump_data(games)


def fetch_runs():
    with open("data/games.json") as f:
        games = json.load(f)

    speedrun_service = SpeedrunService()
    with tqdm(total=len(games), desc="Fetching game runs") as pbar:
        for game in games:
            # Skip games that have already been fetched
            if path.exists(f"data/runs/{game['id']}.json"):
                pbar.update(1)
                continue

            runs = speedrun_service.get_game_runs(game["id"])
            RunJSONDumper(f"{game['id']}.json", speedrun_service).dump_data(runs)
            pbar.update(1)


if __name__ == "__main__":
    fetch_games()
    fetch_runs()
