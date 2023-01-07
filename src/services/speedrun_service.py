import time
from collections import defaultdict

import srcomapi
import srcomapi.datatypes as dt


class PaginationMixin:
    max_results = 200

    def _get_data(self, data_type, params=None):
        raise NotImplementedError

    def _get_all_data(self, data_type, params=None):
        params = params or {}
        current_results = 200
        pagination_params = {
            "max": self.max_results,
            "offset": 0
        }

        while current_results == self.max_results:
            data = self._get_data(data_type, {**pagination_params, **params})
            for item in data:
                yield item
            
            current_results = len(data)
            print(f"Got {pagination_params['offset'] + current_results} results of {data_type.__name__} so far...")
            pagination_params["offset"] += self.max_results


class SpeedrunService(PaginationMixin):
    def __init__(self):
        self.api = srcomapi.SpeedrunCom(user_agent="speedrun-project")
        self._region_mapping = {}

    def _get_data(self, data_type, params=None):
        time.sleep(1)
        return self.api.search(data_type, params or {})

    def get_region_data_id_or_name(self, identifier):
        if identifier is None:
            return None
        if not self._region_mapping:
            for region in self._get_data(dt.Region):
                self._region_mapping[region.id] = region.name
                self._region_mapping[region.name] = region.id
        return self._region_mapping[identifier]

    def get_games(self):
        game_params = {
            "region": self.get_region_data_id_or_name("JPN / NTSC"),
        }
        for game in self._get_all_data(dt.Game, game_params):
            if len(game.regions) >= 2:
                yield game

    def get_game_runs(self, game_id):
        all_runs = self._get_all_data(dt.Run, {"game": game_id, "status": "verified"})
        runs_by_user = defaultdict(list)
        for run in all_runs:
            if not run.players:
                continue

            player = run.players[0]
            runs_by_user[player.name].append(run)

        # Get the fastest run for each user, others are obsolete
        for _, runs in runs_by_user.items():
            runs.sort(key=lambda run: run.times["primary_t"])
            yield runs[0]
