from services.json_loader import GameJSONLoader, RunJSONLoader
import os


def load_data():
    games = GameJSONLoader("games.json").load_data()
    for run_file in os.listdir("data/runs"):
        if not run_file.endswith(".json"):
            continue
        game_id = run_file.removesuffix(".json")
        games[game_id]["runs"] = RunJSONLoader(run_file).load_data()

    return games


def remove_nulled_games(games):
    new_games = {}
    for game_id, game in list(games.items()):
        new_runs = []
        for run in game["runs"]:
            if run["region"] is not None:
                new_runs.append(run)
        if new_runs:
            new_games[game_id] = game

    return new_games


def calculate_total_runs(games):
    return sum(len(game["runs"]) for game in games.values())


def calculate_runs_by_region(games):
    runs_by_region = {}
    for game in games.values():
        for run in game["runs"]:
            region = run["region"]
            runs_by_region[region] = runs_by_region.get(region, 0) + 1
    return runs_by_region


def calculate_top_players(games, region=None, player_location=None):
    player_games = {}
    for game in games.values():
        for run in game["runs"]:
            if region and run["region"] != region:
                continue
            if player_location and run["player_location"] == player_location:
                continue

            player = run["player"]
            player_games[player] = player_games.get(player, 0) + 1

    return player_games


def calculate_top_players_in_jp_region(games):
    return calculate_top_players(games, region="JPN / NTSC")


def calculate_top_non_jp_players_in_jp_region(games):
    return calculate_top_players(games, region="JPN / NTSC", player_location="jp")


def print_top_n(title, data, n=None):
    print(title)
    for player, count in sorted(data.items(), key=lambda x: x[1], reverse=True)[:len(data) if n is None else n]:
        print(f"  {player}: {count}")


def calculate_number_of_runs(games, predicate):
    run_counter = 0
    for game in games.values():
        for run in game["runs"]:
            if predicate(run):
                continue
            run_counter += 1

    return run_counter


def calculate_number_of_games_with_most_runs_by_region(games):
    jp_game_counter = 0
    other_game_counter = 0
    for game in games.values():
        run_region_counter = {}
        for run in game["runs"]:
            region = run["region"]
            run_region_counter[region] = run_region_counter.get(region, 0) + 1
        sorted_stats = sorted(run_region_counter.items(), key=lambda x: x[1], reverse=True)
        if not sorted_stats:
            continue

        current_max = sorted_stats[0][1]

        for stat in sorted_stats:
            if stat[1] < current_max:
                break
            if stat[0] == "JPN / NTSC":
                jp_game_counter += 1
                break

        for stat in sorted_stats:
            if stat[1] < current_max:
                break
            if stat[0] != "JPN / NTSC":
                other_game_counter += 1
                break

    return jp_game_counter, other_game_counter


def calculate_number_of_games_with_most_runs_by_player_region(games):
    jp_game_counter = 0
    other_game_counter = 0
    for game in games.values():
        run_counter_jp_oth = 0
        run_counter_oth_jp = 0
        for run in game["runs"]:
            region = run["region"]
            if region == "JPN / NTSC" and run["player_location"] != "jp":
                run_counter_jp_oth += 1
            elif region != "JPN / NTSC" and run["player_location"] == "jp":
                run_counter_oth_jp += 1

        if run_counter_jp_oth > run_counter_oth_jp:
            jp_game_counter += 1
        elif run_counter_oth_jp > run_counter_jp_oth:
            other_game_counter += 1

    return jp_game_counter, other_game_counter


def generate_statistics():
    # Load games from JSON files and preprocess data
    all_games = load_data()
    games = remove_nulled_games(all_games)
    print(f"Number of games with at least one run with specified system region: {len(games)}")

    # Calculate total number of runs
    total_runs = calculate_total_runs(games)
    print(f"Total number of runs with specified system region: {total_runs}")

    # Calculate number of runs by region
    runs_by_region = calculate_runs_by_region(games)
    print_top_n("Number of runs by region:", runs_by_region)

    # Top 10 players by number of runs
    player_games = calculate_top_players(all_games)
    print_top_n("Top 10 players by number of runs:", player_games, n=10)

    # Top 10 players by number of runs in JP region
    player_games_jp = calculate_top_players_in_jp_region(games)
    print_top_n("Top 10 players by number of runs in JP region:", player_games_jp, n=10)

    # Top 10 non JP players by number of runs in JP region
    non_jp_player_games_jp = calculate_top_non_jp_players_in_jp_region(games)
    print_top_n("Top 10 non JP players by number of runs in JP region:", non_jp_player_games_jp, n=10)

    # Number of runs in JP region by players from other regions
    non_jp_player_jp_runs_count = calculate_number_of_runs(
        games,
        lambda run: run["region"] != "JPN / NTSC" or run["player_location"] == "jp"
    )
    print(f"Number of runs in JP region by players from other regions: {non_jp_player_jp_runs_count}")

    # Number of runs in other regions by players from JP region
    jp_player_non_jp_runs_count = calculate_number_of_runs(
        games,
        lambda run: run["region"] == "JPN / NTSC" or run["player_location"] != "jp"
    )
    print(f"Number of runs in other regions by players from JP region: {jp_player_non_jp_runs_count}")

    # Number of games with most runs in JP region and other regions.
    jp_games_count, other_games_count = calculate_number_of_games_with_most_runs_by_region(games)
    print(f"Number of games with most runs in JP region: {len(games) - other_games_count}")
    print(f"Number of games with most runs in other regions: {len(games) - jp_games_count}")
    print(f"Number of tied games: {abs(len(games) - jp_games_count - other_games_count)}")

    # Number of games with most runs in JP region by players from other regions and vice versa
    jp_games_count, other_games_count = calculate_number_of_games_with_most_runs_by_player_region(games)
    print(f"Number of games with most runs in JP region by players from other regions: {jp_games_count}")
    print(f"Number of games with most runs in other regions by players from JP region: {other_games_count}")
    print(f"Number of tied games: {len(games) - jp_games_count - other_games_count}")

    # TODO number of runs per game distribution graph


if __name__ == "__main__":
    generate_statistics()
