import requests


class SpeedrunComClient:
    API_URL = "https://www.speedrun.com/api/v1/"

    def __init__(self, user_agent="speedrun-project"):
        self.headers = {"User-Agent": user_agent}

    def get_runs(self, game_id, **params):
        return self._get("runs", game=game_id, **params)

    def get_games(self, **params):
        return self._get("games", **params)

    def get_regions(self, **params):
        return self._get("regions", **params)

    def _get(self, endpoint, **params):
        uri = f"{self.API_URL}{endpoint}"
        response = requests.get(uri, headers=self.headers, params=params)
        if not response.ok:
            raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

        return response.json()["data"]
