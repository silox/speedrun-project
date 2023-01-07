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


def generate_statistics():
    # Load games from JSON files
    games = load_data()

    # Calculate total number of runs
    total_runs = sum(len(game["runs"]) for game in games.values())
    print(f"Total number of runs: {total_runs}")

    # Calculate number of runs by region
    runs_by_region = {}
    for game in games.values():
        for run in game["runs"]:
            region = run["region"]
            runs_by_region[region] = runs_by_region.get(region, 0) + 1
    
    print("Number of runs by region:")
    for region, count in sorted(runs_by_region.items(), key=lambda x: x[1], reverse=True):
        print(f"  {region}: {count}")
    
    # Top 10 players by number of runs
    player_games = {}
    for game in games.values():
        for run in game["runs"]:
            player = run["player"]
            player_games[player] = player_games.get(player, 0) + 1
    
    print("Top 10 players by number of runs:")
    for player, count in sorted(player_games.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {player}: {count}")

    # Top 10 players by number of runs in JP region
    player_games = {}
    for game in games.values():
        for run in game["runs"]:
            if run["region"] != "JPN / NTSC":
                continue

            player = run["player"]
            player_games[player] = player_games.get(player, 0) + 1
    
    print("Top 10 players by number of runs in JP region:")
    for player, count in sorted(player_games.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {player}: {count}")

    # Top 10 non JP players by number of runs in JP region
    player_games = {}
    for game in games.values():
        for run in game["runs"]:
            if run["region"] != "JPN / NTSC" or run["player_location"] == "jp":
                continue

            player = run["player"]
            player_games[player] = player_games.get(player, 0) + 1
    
    print("Top 10 players by number of runs in JP region:")
    for player, count in sorted(player_games.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {player}: {count}")

    # Number of runs in JP region by players from other regions
    run_counter = 0
    for game in games.values():
        for run in game["runs"]:
            if run["region"] != "JPN / NTSC" or run["player_location"] == "jp":
                continue

            run_counter += 1
    
    print(f"Number of runs in JP region by players from other regions: {total_runs}")

    # Number of runs in other regions by players from JP region
    run_counter = 0
    for game in games.values():
        for run in game["runs"]:
            if run["region"] == "JPN / NTSC" or run["player_location"] != "jp":
                continue

            run_counter += 1
    
    print(f"Number of runs in other regions by players from JP region: {total_runs}")

    # Number of games with most runs in JP region and other regions.
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
    
    print(f"Number of games with most runs in JP region: {len(games) - other_game_counter}")
    print(f"Number of games with most runs in other regions: {len(games) - jp_game_counter}")
    print(f"Number of tied games: {abs(len(games) - jp_game_counter - other_game_counter)}")

    # Number of games with most runs in JP region by players from other regions and vice versa
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

    print(f"Number of games with most runs in JP region by players from other regions: {jp_game_counter}")
    print(f"Number of games with most runs in other regions by players from JP region: {other_game_counter}")
    print(f"Number of tied games: {len(games) - jp_game_counter - other_game_counter}")

    # TODO number of runs per game distribution graph

if __name__ == "__main__":
    generate_statistics()
