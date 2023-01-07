import time
from collections import defaultdict

from clients.speedrun_client import SpeedrunComClient


class PaginationMixin:
    max_results = 200

    def _get_data(self, content_method, params=None):
        raise NotImplementedError

    def _get_all_data(self, content_method, params=None):
        params = params or {}
        current_results = 200
        pagination_params = {
            "max": self.max_results,
            "offset": 0
        }

        while current_results == self.max_results:
            data = self._get_data(content_method, {**pagination_params, **params})
            for item in data:
                yield item
            
            current_results = len(data)
            print(f"Got {pagination_params['offset'] + current_results} results so far...")
            pagination_params["offset"] += self.max_results

            # Speedrun api has a limit of 10k results (there are around 13 games with more than 10k runs)
            if pagination_params["offset"] >= 10000:
                return


class SpeedrunService(PaginationMixin):
    def __init__(self):
        self.client = SpeedrunComClient(user_agent="speedrun-project")
        self._region_mapping = {}

    def _get_data(self, content_method, params=None):
        time.sleep(0.6)
        return getattr(self.client, content_method)(**(params or {}))

    def get_region_data_id_or_name(self, identifier):
        """
        Store the region data in a mapping to avoid making multiple requests for the same data
        and return the id or name of the region depending on the identifier
        """
        if identifier is None:
            return None
        if not self._region_mapping:
            for region in self._get_data("get_regions"):
                self._region_mapping[region["id"]] = region["name"]
                self._region_mapping[region["name"]] = region["id"]
        return self._region_mapping[identifier]

    def get_games_with_jp_region(self):
        """
        Get all games that have the Japanese region and at least one other region
        """
        game_params = {
            "region": self.get_region_data_id_or_name("JPN / NTSC"),
        }
        for game in self._get_all_data("get_games", game_params):
            if len(game["regions"]) >= 2:
                yield game

    def get_game_runs(self, game_id):
        all_runs = self._get_all_data("get_runs", {"game_id": game_id, "status": "verified", "embed": "players"})
        runs_by_user = defaultdict(list)
        for run in all_runs:
            players = run["players"]["data"]
            if not players:
                continue

            if players[0]["rel"] == "guest":
                runs_by_user[players[0]["name"]].append(run)
            else:
                runs_by_user[players[0]["names"]["international"]].append(run)

        # Get the fastest run for each user, others are obsolete
        for _, runs in runs_by_user.items():
            runs.sort(key=lambda run: run["times"]["primary_t"])
            yield runs[0]
