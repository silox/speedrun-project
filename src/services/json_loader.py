import json
import os


class JSONLoader():
    data_dir = ""

    def __init__(self, json_file):
        self.json_file = json_file

    def load_data(self):
        file_name = f"data/{self.data_dir}{self.json_file}"
        if not os.path.exists(file_name):
            print(f"File {file_name} does not exist. You must fetch data to generate statistics.")
            print("Run `python src/fetch_data.py` to fetch data.")

        with open(file_name) as f:
            return self.process_data(json.load(f))

    def process_data(self, data):
        return data


class GameJSONLoader(JSONLoader):
    def process_data(self, games_data):
        return {game["id"]: {"name": game["name"], "runs": []} for game in games_data}


class RunJSONLoader(JSONLoader):
    data_dir = "runs/"

    def process_data(self, runs_data):
        for run in runs_data:
            del run["id"]
        return runs_data
