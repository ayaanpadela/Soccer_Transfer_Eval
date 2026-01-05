# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import config

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    stat_type= "Shooting"
    season="2021"
    print(f"{config.DATA_DIR}player_stats_{stat_type}_{season}.csv")  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
