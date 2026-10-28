from pathlib import Path
import time

import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog

# FIND LEBRON
results = players.find_players_by_full_name("LeBron James")

if not results:
    raise RuntimeError("LeBron James not found")

lebron = next(
    player for player in results
    if player["full_name"] == "LeBron James"
)

player_id = lebron["id"]


# SEASONS 2015-16 TO 2025-26
seasons = [
    "2015-16",
    "2016-17",
    "2017-18",
    "2018-19",
    "2019-20",
    "2020-21",
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26"
]

dataframes = []

for season in seasons:
    print(f"Getting data from season {season}")
    
    try:
        response = playergamelog.PlayerGameLog(
            player_id=player_id,
            season=season,
            season_type_all_star="Regular Season",
            timeout=60,
        )
        
        df = response.get_data_frames()[0]
        
        if df.empty:
            print(f"No data available for season {season}")
            continue
    
        dataframes.append(df)
        print(f"{len(df)} games obtained.")
    
    except Exception as error:
        print(f"Error at season {season}: {error}")
        
    time.sleep(1) # avoiding too much requests


if not dataframes:
    raise RuntimeError("Unable to get data. Check your connection")


# JOINING THE SEASONS
history = pd.concat(dataframes, ignore_index=True)

# avoid duplicates
history = history.drop_duplicates(subset=["Game_ID"])

# chronological order
history["GAME_DATE"] = pd.to_datetime(
    history["GAME_DATE"],
    errors="coerce"
)

history = history.sort_values("GAME_DATE").reset_index(drop=True)


# CREATE OUTPUT DIRECTORY
output_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
output_dir.mkdir(parents=True, exist_ok=True)


# EXPORT CSV
output_file = output_dir / "lebron_game_logs.csv"

history.to_csv(
    output_file,
    index=False,
    encoding="utf-8"
)

print("==================================================")
print("\nDownload concluded.")
print(f"Total games: {len(history)}")
print(f"File saved at: {output_file}")
print("==================================================")
print("\nPre-visualization:")
print(history.head())

print(f"\nAvailable columns: {history.columns.tolist()}")