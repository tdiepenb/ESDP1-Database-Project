import sys
import numpy as np
import pandas as pd
from ftplib import FTP
import requests   # more convenient for http(s) urls
import numpy as np
import os
from import_export_data import download_years

from import_export_data import download_years
from import_export_data import export_downloaded_years
from database_handling import create_connection
from database_handling import create_table
from database_handling import insert_copy

possible_years = np.arange(1949, 2020, 1)

def is_valid_year(year):
    """Check if the given year is a valid integer within a reasonable range."""
    try:
        year = int(year)
        if year in possible_years:  
            return True
        else:
            return False
    except ValueError:
        return False

if __name__ == "__main__":

    years = [1949, 1950]

    for year in years:
        file_path_base = f"./data/climate/script"
        download_years(years=years,file_path="data/climate/script")

        export_downloaded_years(years=years, file_path_source=f"./data/climate/script/{year}.csv.gz", file_path_dest="./data/climate/script")

        table_name = f"climate{year}"

        column_specs = f'''
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            id SERIAL PRIMARY KEY,
                            stationcode VARCHAR(50),
                            datelabel DATE,
                            param VARCHAR(10),
                            value FLOAT,
                            mflag VARCHAR(10),
                            qflag VARCHAR(10),
                            sflag VARCHAR(10),
                            time
                        )
                    '''
        
        # create_connection(dbname="mydatabase", user="myuser", password="mypassword", host="localhost", port="5432")

        create_table(tablename = table_name, columnspecs = column_specs)

        cols = ["id", "stationcode", "datelabel", "param", "value", "mflag", "qflag", "sflag", "time"]

        insert_copy(file_path=f"{file_path_base}/modified_{year}.csv", table_name=table_name, columns=cols)
    


# def import_data_dialog():
#     print("Importing data...")
#     # Implement data import functionality here

#     years = []

#     choice = input("Enter the years you want to import (comma seperated) ")
#     years_input = choice.split(",")
    

#     for year in years_input:
#         year_check = year.strip()
#         if(is_valid_year(year_check)):
#             years.append(int(year_check))

#     print(years)

#     choice = input(f"The years you selected are: {years}. \n Do you want to download them? (Type Y for yes or N for no)")

#     if choice in ("Y", "y"):
#         print("Download")
#         download_years(years)
#     elif choice in ("N", "n"):
#         print("Cancel")
#         main_menu()
#     else: 
#         print("Cancel")
#         main_menu()
        

#     # sys.exit()

# def export_data():
#     print("Exporting data...")
#     # Implement data export functionality here

# def visualize_data():
#     print("Visualizing data...")
#     # Implement data visualization functionality here

# def main_menu():
#     while True:
#         print("\nInteractive Python App")
#         print("1. Import Data")
#         print("2. Export Data")
#         print("3. Visualize Data")
#         print("4. Exit")

#         choice = input("Enter your choice: ")

#         if choice == '1':
#             import_data_dialog()
#         elif choice == '2':
#             export_data()
#         elif choice == '3':
#             visualize_data()
#         elif choice == '4':
#             print("Exiting...")
#             sys.exit()
#         else:
#             print("Invalid choice, please try again.")