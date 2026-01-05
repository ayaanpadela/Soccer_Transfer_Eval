import soccerdata as sd
import pandas as pd
import warnings
import config
import os
warnings.filterwarnings('ignore')
def scrape_season_stats(season):
    print("Scraping Season Stats for " + season)
    try :
        fbref = sd.FBref(leagues=config.LEAGUES, seasons=season)
        season_data= {}
        stat_types= ["standard","shooting","passing"]
        for stat in stat_types:
            print(f"Scraping Stats for {stat}")
            df= fbref.read_player_season_stats(stat_type=stat)
            season_data[stat] = df
        return season_data

    except :
        print(f"Error scraping Season Stats for {season}")
        return None

def main():
    print("Starting Player stats scraping")
    for season in config.SEASONS:
        season_data = scrape_season_stats(season)
        if season_data :
            for stat_type,df in season_data.items():
                filename= f"{config.DATA_DIR}player_stats/{stat_type}_{season}.csv"
                df.to_csv(filename)
                print(f"{stat_type} stats saved")
if __name__ == "__main__":
    main()