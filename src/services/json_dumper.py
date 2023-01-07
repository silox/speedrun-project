import abc
import json
from pathlib import Path

from services.speedrun_service import SpeedrunService


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
            "player": player_name,
            "player_location": player_location,
            "region": self.speedrun_service.get_region_data_id_or_name(run["system"]["region"]),
        }
