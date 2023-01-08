import abc
import json
from pathlib import Path


class JSONDumper(abc.ABC):
    data_dir = ""

    def __init__(self, json_file):
        self.json_file = json_file

    def dump_data(self, obj_data, indent=2):
        Path(f"data/{self.data_dir}").mkdir(parents=True, exist_ok=True)

        with open(f"data/{self.data_dir}{self.json_file}", "w") as f:
            data = [self.process_obj(obj) for obj in obj_data]
            json.dump(data, f, indent=indent)

    @abc.abstractmethod
    def process_obj(self, obj_data):
        return NotImplemented


class GameJSONDumper(JSONDumper):
    def process_obj(self, game):
        return {
            "id": game["id"],
            "name": game["names"]["international"],
        }


class RunJSONDumper(JSONDumper):
    data_dir = "runs/"

    def __init__(self, json_file, speedrun_service):
        self.speedrun_service = speedrun_service
        super().__init__(json_file)

    def process_obj(self, run):
        players = run["players"]["data"]
        player = players[0] if players else None
        try:
            player_name = player["names"]["international"] if player["rel"] == "user" else player["name"]
        except Exception:
            player_name = None
        try:
            player_location = player["location"]["country"]["code"]
        except Exception:
            player_location = None

        return {
            "id": run["id"],
            "game": self.speedrun_service.get_game_name(run["game"]),
            "player": player_name,
            "player_location": player_location,
            "time": run["times"]["primary_t"],
            "category": self.speedrun_service.get_category_name(run["category"]),
            "region": self.speedrun_service.get_region_data_id_or_name(run["system"]["region"]),
            "platform": self.speedrun_service.get_platform_name(run["system"]["platform"]),
            "emulated": run["system"]["emulated"],
        }
