import Players_Scrape
import Transfers_Scrape
import Wages_Scrape
import os
import config


def main():
    print("=== Soccer Transfer Evaluation Data Pipeline ===")

    # Ensure data directory exists
    if not os.path.exists(config.DATA_DIR):
        os.makedirs(config.DATA_DIR)
        print(f"Created directory: {config.DATA_DIR}")

    # 1. Scrape Player Stats
    print("\n--- Step 1: Scraping Player Stats ---")
    Players_Scrape.main()

    # 2. Scrape Transfers
    print("\n--- Step 2: Scraping Transfers ---")
    Transfers_Scrape.main()

    # 3. Scrape Wages
    print("\n--- Step 3: Scraping Wages ---")
    Wages_Scrape.main()

    print("\n=== Data Pipeline Completed Successfully ===")


if __name__ == "__main__":
    main()