import soccerdata as sd
import pandas as pd

# Same scope
leagues = ['ENG-Premier League', 'ESP-La Liga', 'ITA-Serie A', 'GER-Bundesliga', 'FRA-Ligue 1']
seasons = [str(year) for year in range(2017, 2024)]

print("Initializing FBref scraper...")
fbref = sd.FBref(leagues=leagues, seasons=seasons)

# We need multiple 'stat types' to get a complete picture
# 'standard': Goals, Assists, Minutes
# 'shooting': npxG, Shots
# 'passing': Progressive Passes, Key Passes
stat_types = ['standard', 'shooting', 'passing']

for stat in stat_types:
    print(f"Scraping {stat} stats...")
    df = fbref.read_player_season_stats(stat_type=stat)

    # Save each type to a separate CSV for now
    filename = f"data_fbref_{stat}.csv"
    df.to_csv(filename)
    print(f"Saved {filename}")

print("Performance data collection complete.")