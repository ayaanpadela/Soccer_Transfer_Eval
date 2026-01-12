import requests
import pandas as pd
import time
import random
import os
import config
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
TM_LEAGUES = {
    'ENG-Premier League': {'url_name': 'premier-league', 'id': 'GB1'},
    'ESP-La Liga': {'url_name': 'laliga', 'id': 'ES1'},
    'GER-Bundesliga': {'url_name': 'bundesliga', 'id': 'L1'},
    'ITA-Serie A': {'url_name': 'serie-a', 'id': 'IT1'},
    'FRA-Ligue 1': {'url_name': 'ligue-1', 'id': 'FR1'}
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}


def get_season_year(season_str):
    """Converts '1718' -> '2017'"""
    return "20" + season_str[:2]


def clean_money(val):
    """
    Cleans Transfermarkt money strings.
    Handles: "€150.00m", "€500k", "free transfer", "Loan fee: €2.00m", "End of loan"
    Returns: Float (in Euros) or 0.
    """
    if pd.isna(val) or val == "-" or val == "?" or val == "":
        return 0.0

    val = str(val).lower().strip()

    # If no numbers are present, it's likely a free transfer or end of loan with no fee
    has_digits = any(char.isdigit() for char in val)
    if not has_digits:
        return 0.0

    # Remove clutter words but keep the numbers and multipliers
    val = val.replace('loan fee:', '').replace('loan', '').replace('free transfer', '').replace('?', '')
    val = val.replace('€', '').replace('£', '').replace('$', '').replace(',', '')

    multiplier = 1.0
    if 'm' in val:
        multiplier = 1_000_000
        val = val.replace('m', '')
    elif 'k' in val or 'th.' in val:
        multiplier = 1_000
        val = val.replace('k', '').replace('th.', '')

    try:
        return float(val.strip()) * multiplier
    except ValueError:
        return 0.0


def scrape_league_transfers(league_key, season_str):
    league_info = TM_LEAGUES[league_key]
    year = get_season_year(season_str)

    # Use the "plus" view for detailed data (market value, specific positions)
    url = f"https://www.transfermarkt.com/{league_info['url_name']}/transfers/wettbewerb/{league_info['id']}/plus/?saison_id={year}"
    print(f"  > Fetching URL: {url}...")

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        all_transfers = []

        # Clubs are typically in 'box' divs
        boxes = soup.find_all("div", class_="box")
        club_boxes = boxes[3:23]
        for box in boxes:
            # Extract Club Name from header
            header = box.find("h2", class_="content-box-headline")
            if not header:
                continue

            # The club name is usually in an <a> tag inside the H2
            club_link = header.find("a")
            if not club_link or not club_link.get("title"):
                continue

            club_name = club_link.get("title")

            # 3. Find tables inside this specific box
            tables = box.find_all("table")
            if not tables:
                continue

            for table in tables:
                thead = table.find("thead")
                if not thead: continue

                header_cells = thead.find_all("th")
                headers = [th.get_text(strip=True) for th in header_cells]

                # # Dynamic Column Mapping
                # col_map = {}
                # for i, h in enumerate(headers):
                #     if "Player" in h or h == "": # Player column is often index 1, index 0 is photo
                #         if 'Player' not in col_map: col_map['Player'] = i
                #     elif "Age" in h: col_map['Age'] = i
                #     elif "Nat" in h: col_map['Nat'] = i
                #     elif "Pos" in h: col_map['Pos'] = i
                #     elif "Market value" in h: col_map['Market_Value'] = i
                #     elif "Left" in h or "Joined" in h: col_map['Counterpart_Club'] = i
                #     elif "Fee" in h: col_map['Fee'] = i

                # Determine direction (In/Out)
                direction = "Unknown"
                if "Left" in headers:
                    direction = "In"
                elif "Joined" in headers:
                    direction = "Out"
                tbody = table.find('tbody')
                trs = tbody.find_all('tr')
                for tr in trs:
                    player_str = tr.get_text(separator='/', strip=True)
                    player_list = player_str.split(sep='/')
                    # print(player_list)
                    player_name = player_list[0]
                    player_mv = player_list[5]
                    player_club = player_list[6]
                    player_fee = player_list[7]
                    all_transfers.append({
                        "League": league_key,  # Fixed Syntax Error
                        "Season": f"{year}-{int(year) + 1}",
                        "Club": club_name,
                        "Direction": direction,
                        "Player": player_name,
                        "Counterpart_Club": player_club,
                        "Market_Value_Raw": player_mv,
                        "Market_Value_Cleaned": clean_money(player_mv),
                        "Fee_Raw": player_fee,
                        "Fee_Cleaned": clean_money(player_fee)
                    })
                # Parse Rows
                # rows = table.find_all("tr", class_=("odd", "even"))
                # for row in rows:
                #     cols = row.find_all("td")
                #     if not cols or len(cols) < max(col_map.values()):
                #         continue

                #     try:
                #         # Player Name extraction
                #         name_cell = cols[col_map['Player']]
                #         # Look for specific profil link
                #         p_link = name_cell.find("a", href=re.compile(r"/profil/spieler/"))
                #         player_name = p_link.get_text(strip=True) if p_link else name_cell.get_text(strip=True)

                #         if not player_name or player_name.lower() in ["none", "no arrivals", "no departures"]:
                #             continue

                #         # Data collection using the map
                #         age = cols[col_map['Age']].get_text(strip=True) if 'Age' in col_map else "Unknown"

                #         nat_cell = cols[col_map['Nat']] if 'Nat' in col_map else None
                #         nat_imgs = nat_cell.find_all("img") if nat_cell else []
                #         nationality = nat_imgs[0]['title'] if nat_imgs else "Unknown"

                #         position = cols[col_map['Pos']].get_text(strip=True) if 'Pos' in col_map else "Unknown"
                #         market_val_raw = cols[col_map['Market_Value']].get_text(strip=True) if 'Market_Value' in col_map else "0"

                #         counterpart_cell = cols[col_map['Counterpart_Club']] if 'Counterpart_Club' in col_map else None
                #         cp_link = counterpart_cell.find("a") if counterpart_cell else None
                #         counterpart_club = cp_link.get_text(strip=True) if cp_link else "Unknown"

                #         fee_raw = cols[col_map['Fee']].get_text(strip=True)

                #     except Exception:
                #         continue

        if all_transfers:
            return pd.DataFrame(all_transfers)
        else:
            print("    ! No valid transfers parsed from the page.")
            return None

    except Exception as e:
        print(f"    !! Error: {e}")
        return None


def main():
    print("--- STARTING ROBUST TRANSFERMARKT SCRAPER (BS4) ---")

    output_dir = f"{config.DATA_DIR}Transfers/"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for season in config.SEASONS:
        print(f"\n[Season: {season}]")

        for league_key in config.LEAGUES:
            clean_league_name = league_key.split('-')[1]
            filename = f"{output_dir}transfers_{clean_league_name}_{season}.csv"

            # Safety check: skip if we already have it
            if os.path.exists(filename):
                print(f"  [SKIP] {clean_league_name} {season} already exists.")
                continue

            df = scrape_league_transfers(league_key, season)

            if df is not None:
                df.to_csv(filename, index=False)
                print(f"    + Saved {len(df)} rows to {filename}")

            # Random sleep to mimic human behavior
            wait = random.uniform(5, 12)
            time.sleep(wait)


if __name__ == "__main__":
    main()
