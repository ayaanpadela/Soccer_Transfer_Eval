import soccerdata as sd
import pandas as pd
import warnings
import config
import os

warnings.filterwarnings('ignore')

def scrape_season_stats(season):
    print("Scraping Season Stats for " + season)
    try:
        fbref = sd.FBref(leagues=config.LEAGUES, seasons=season)
        season_data = {}
        # Define the stats you are collecting here so we can reference them in main() as well
        stat_types = ["standard", "shooting", "passing"]
        for stat in stat_types:
            print(f"Scraping Stats for {stat}")
            df = fbref.read_player_season_stats(stat_type=stat)
            season_data[stat] = df
        return season_data

    except Exception as e:
        print(f"Error scraping Season Stats for {season}: {e}")
        return None

def main():
    print("Starting Player stats scraping")
    # Ensure directory exists
    output_dir = f"{config.DATA_DIR}player_stats/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define stats types again or import them from config if preferred
    stat_types = ["standard", "shooting", "passing"]

    for season in config.SEASONS:
        # --- NEW CHECK: Skip if files exist ---
        # We check if ALL stat types for this season are already saved
        existing_files = [f"{output_dir}{stat}_{season}.csv" for stat in stat_types]
        if all(os.path.exists(f) for f in existing_files):
            print(f"Skipping {season}: All data files already exist.")
            continue
        # ---------------------------------------

        season_data = scrape_season_stats(season)
        if season_data:
            for stat_type, df in season_data.items():
                filename = f"{output_dir}{stat_type}_{season}.csv"
                df.to_csv(filename)
                print(f"{stat_type} stats saved for {season}")

if __name__ == "__main__":
    main()