import soccerdata as sd
import time
import random
import warnings
warnings.filterwarnings('ignore')
leagues = ['ENG-Premier League', 'ESP-La Liga', 'FRA-Ligue 1', 'GER-Bundesliga', 'ITA-Serie A']
seasons = ["1718", "1819", "1920", "2021", "2122", "2223", "2324"]
stat_types = ["standard", "shooting", "passing"]

print("--- STARTING FBREF SCRAPE (Estimated Time: 10 mins) ---")

for season in seasons:
    print(f"\n[Processing Season: {season}]")

    try:
        fbref = sd.FBref(leagues=leagues, seasons=[season])

        for stat in stat_types:
            print(f"  > Fetching {stat} stats...")
            df = fbref.read_player_season_stats(stat_type=stat)

            filename = f"data/fbref_{stat}_{season}.csv"
            df.to_csv(filename)
            print(f"    Saved {filename}")

            # Short pause between stat types
            time.sleep(random.uniform(5, 10))

    except Exception as e:
        print(f"ERROR on {season}: {e}")

    # LONG PAUSE between seasons to reset IP "heat"
    print("Pausing in between to prevent IP ban")
    time.sleep(30)

print("\n Player SCRAPE COMPLETE")