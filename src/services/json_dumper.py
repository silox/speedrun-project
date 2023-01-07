import abc
import json
from pathlib import Path

from services import SpeedrunService


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
            "id": game.id,
            "name": game.names["international"],
        }

class RunJSONDumper(JSONDumper):
    data_dir = "runs/"

    def __init__(self, json_file):
        self.speedrun_service = SpeedrunService()
        super().__init__(json_file)

    def process_obj(self, run):
        return {
            "id": run.id,
            "player": (player := run.players[0]).name,
            "player_location": player.location["country"]["code"] if hasattr(player, "location") and player.location else None,
            "region": self.speedrun_service.get_region_data_id_or_name(run.system["region"]),
        }
