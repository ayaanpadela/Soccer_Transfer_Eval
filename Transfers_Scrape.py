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
    return season_str[:2]+"/"+season_str[2:4]


def scrape_transfers():
    transfer_markt= sfc.Transfermarkt()
    # Ensure directory exists
    output_dir = f"{config.DATA_DIR}Transfers/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Loop through our mapped leagues
    for league in config.ScraperFC_Leagues:
        for season_str in config.SEASONS:
            season_str = get_start_year(season_str)

            filename = f"{output_dir}transfers_{league}_{season_str.replace('/', '_')}.csv"

            # 1. Check if exists
            if os.path.exists(filename):
                print(f"[SKIP] Transfer for {league} {season_str} exists.")
                continue

            print(f"\n[Scraping Transfer] {league} ({season_str})...")

            try:
                # Scrape
                df=transfer_markt.scrape_players(season_str,league)
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
    print("--- STARTING Transfer PIPELINE ---")
    scrape_transfers()
if __name__ == "__main__":
    main()