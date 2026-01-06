import ScraperFC as sfc
import pandas as pd
import time
import random
import os
import config
import warnings

warnings.filterwarnings('ignore')


def get_start_year(season_str):
    """Converts '1718' -> 2017-18"""
    return str(2000 + int(season_str[:2]))+"-"+str(int(season_str[2:]))


def scrape_wages():
    capology = sfc.Capology()
    # Ensure directory exists
    output_dir = f"{config.DATA_DIR}wages/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Loop through our mapped leagues
    for league in config.CAPOLOGY_LEAGUES:
        for season_str in config.SEASONS:
            season_str = get_start_year(season_str)
            # Construct filename: data/wages/wages_Premier League_2017.csv
            # We use the standard name in the filename to keep it clean
            # 'Premier League' from 'ENG-Premier League'
            filename = f"{output_dir}wages_{league}_{season_str}.csv"

            # 1. Check if exists
            if os.path.exists(filename):
                print(f"[SKIP] Wages for {league} {season_str} exists.")
                continue

            print(f"\n[Scraping Wages] {league} ({season_str})...")

            try:
                # Scrape
                df = capology.scrape_salaries(year=season_str, league=league, currency="eur")

                # Add Metadata (Crucial for joining later!)
                df['Season_Str'] = season_str
                df['League_Standard'] = league

                # Save
                df.to_csv(filename, index=False)
                print(f"  + Saved {filename}")

                # 2. Safety Sleep
                time.sleep(random.uniform(5, 10))

            except Exception as e:
                print(f"!! Failed: {league} {season_str} - {e}")


def main():
    print("--- STARTING WAGE PIPELINE ---")
    scrape_wages()

if __name__ == "__main__":
    main()