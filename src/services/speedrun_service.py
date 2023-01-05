import srcomapi
import srcomapi.datatypes as dt


class SpeedrunService:
    def __init__(self):
        self.api = srcomapi.SpeedrunCom()

    def get_game(self):
        return self.api.search(dt.Game, {"name": "super mario sunshine"})
