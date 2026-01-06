import requests
import pandas as pd
import time
import random
import os
import config

# --- CONFIGURATION ---
# Transfermarkt League IDs (These are constant and required for the URL)
TM_LEAGUES = {
    'ENG-Premier League': {'url_name': 'premier-league', 'id': 'GB1'},
    'ESP-La Liga': {'url_name': 'laliga', 'id': 'ES1'},
    'GER-Bundesliga': {'url_name': 'bundesliga', 'id': 'L1'},
    'ITA-Serie A': {'url_name': 'serie-a', 'id': 'IT1'},
    'FRA-Ligue 1': {'url_name': 'ligue-1', 'id': 'FR1'}
}

# Headers are REQUIRED to fool Transfermarkt into thinking we are a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}


def get_season_year(season_str):
    """Converts '1718' -> '2017'"""
    return "20" + season_str[:2]


def scrape_league_transfers(league_key, season_str):
    league_info = TM_LEAGUES[league_key]
    year = get_season_year(season_str)

    # Construct the "Overview" URL
    # Example: transfermarkt.com/premier-league/transfers/wettbewerb/GB1/plus/?saison_id=2023
    url = f"https://www.transfermarkt.com/{league_info['url_name']}/transfers/wettbewerb/{league_info['id']}/plus/?saison_id={year}"

    print(f"  > Fetching URL: {url}...")

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Check for 404/429 errors

        # Pandas reads the HTML and finds ALL tables on the page
        dfs = pd.read_html(response.text)

        # Transfermarkt puts many tables on one page (one per team).
        # We filter for tables that look like transfer lists.
        all_team_transfers = []

        for df in dfs:
            # Check for columns that typically appear in transfer tables
            # Note: Column names change slightly based on the page layout,
            # usually 'Fee', 'Left', 'Joined', or 'Market value' are good indicators.
            if 'Fee' in df.columns or 'Market value' in df.columns:
                # Add metadata so we know where this data came from
                df['League'] = league_key
                df['Season'] = season_str

                # Basic cleaning: Remove empty rows
                df = df.dropna(how='all')

                all_team_transfers.append(df)

        if all_team_transfers:
            # Combine all small team tables into one big league table
            final_df = pd.concat(all_team_transfers, ignore_index=True)
            return final_df
        else:
            print("    ! No valid transfer tables found on page.")
            return None

    except Exception as e:
        print(f"    !! Error: {e}")
        return None


def main():
    print("--- STARTING CUSTOM TRANSFERMARKT SCRAPER ---")

    output_dir = f"{config.DATA_DIR}Transfers/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for season in config.SEASONS:
        print(f"\n[Season: {season}]")

        for league_key in config.LEAGUES:
            # 1. Check if file exists first
            clean_league_name = league_key.split('-')[1]  # 'Premier League'
            filename = f"{output_dir}transfers_{clean_league_name}_{season}.csv"

            if os.path.exists(filename):
                print(f"  [SKIP] {clean_league_name} {season} exists.")
                continue

            # 2. Scrape
            df = scrape_league_transfers(league_key, season)

            if df is not None:
                df.to_csv(filename, index=False)
                print(f"    + Saved {len(df)} rows to {filename}")

            # 3. Sleep to avoid IP Ban (Crucial)
            wait = random.uniform(5, 10)
            time.sleep(wait)


if __name__ == "__main__":
    main()