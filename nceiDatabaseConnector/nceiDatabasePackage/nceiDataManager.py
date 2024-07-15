import os
import requests
import pandas as pd
import numpy as np
from decimal import Decimal


class NCEIDataManager:
    def download_stations(self, file_path_dest="./data/stations/"):
        """
        This function downloads the stations information (readme and ghcnd-stations.txt file) from the NCEI website and saves it in the specified directory

        :param file_path_dest: directory where the stations information will be saved
        :return:
        """
        url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
        response = requests.get(url)
        if response.ok:
            filename = url.rsplit('/', 1)[1]
            print(f"Data downloaded. Will be saved as {filename} in {file_path_dest}")
            os.makedirs(file_path_dest, exist_ok=True)
            with open(f"{file_path_dest}{filename}", "wb") as f:
                f.write(response.content)
        else:
            print("An error occurred while trying to retrieve the data from the internet.")

        url = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt"
        response = requests.get(url)
        if response.ok:
            filename = url.rsplit('/', 1)[1]
            print(f"Data downloaded. Will be saved as {filename} in {file_path_dest}")
            os.makedirs(file_path_dest, exist_ok=True)
            with open(f"{file_path_dest}{filename}", "wb") as f:
                f.write(response.content)
        else:
            print("An error occurred while trying to retrieve the data from the internet.")

        print("Data downloaded and saved in", file_path_dest)
        return

    def convert_stations(self, file_path="./data/stations/", file_path_dest="./data/modifiedStations/"):
        """
        This converts the ghcnd-stations.txt file to a csv file that we can load into the database

        :param file_path: The file path where the original ghcnd-stations.txt file is located
        :param file_path_dest: The path where the modified station file should be saved
        :return:
        """

        # two helper functions
        def conv_str(x):
            return str(x)

        def conv_float(x):
            return float(x)

        # we get this information from the readme.txt file
        column_specs = [
            (0, 11),  # ID
            (12, 20),  # LATITUDE
            (21, 30),  # LONGITUDE
            (31, 37),  # ELEVATION
            (38, 40),  # STATE
            (41, 71),  # NAME
            (72, 75),  # GSN FLAG
            (76, 79),  # HCN/CRN FLAG
            (80, 85)  # WMO ID
        ]
        column_names = [
            'ID', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'STATE', 'NAME',
            'GSN FLAG', 'HCN/CRN FLAG', 'WMO ID'
        ]

        col_conv = {'ID': conv_str,
                    'LATITUDE': conv_float,
                    'LONGITUDE': conv_float,
                    'ELEVATION': conv_float,
                    'STATE': conv_str,
                    'NAME': conv_str,
                    'GSN FLAG': conv_str,
                    'HCN/CRN FLAG': conv_str,
                    'WMO ID': conv_str,
                    }

        path_to_file = f"{file_path}ghcnd-stations.txt"
        df = pd.read_fwf(path_to_file, colspecs=column_specs, names=column_names, converters=col_conv)
        rename_columns = {
            'ID': 'code',
            'LATITUDE': 'lat',
            'LONGITUDE': 'lon',
            'ELEVATION': 'elevation',
            'STATE': 'state',
            'NAME': 'name',
            'GSN FLAG': 'flag1',
            'HCN/CRN FLAG': 'flag2',
            'WMO ID': 'wmo_id'
        }

        df.rename(columns=rename_columns, inplace=True)

        df['wmo_id'] = df['wmo_id'].astype(str)
        df.replace(['None', 'nan'], np.nan, inplace=True)
        df = df.fillna('')

        os.makedirs(file_path_dest, exist_ok=True)
        df.to_csv(f"{file_path_dest}/modified_stations.csv", index=False)
        print(f"Saved the modified stations file to {file_path_dest}/modified_stations.csv")
        return

    def download_years(self, array_of_years=None, file_path="./data/climate/script"):
        """
        This function downloads the specified years from the NCEI website and saves them in a csv file in the specified directory

        :param array_of_years: an array of years to download
        :param file_path: the directory to save the csv files
        :return:
        """

        if array_of_years is None:
            array_of_years = [1994]

        for year in array_of_years:
            print(f"...Downloading data from year {year}....")
            url = f"https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_year/{year}.csv.gz"
            response = requests.get(url)
            if response.ok:
                filename = url.rsplit('/', 1)[1]
                print(f"Data downloaded. Will be saved as {filename}")
                directory_path = file_path
                os.makedirs(directory_path, exist_ok=True)
                with open(f"{file_path}{filename}", "wb") as f:
                    f.write(response.content)
            else:
                print("An error occurred while trying to retrieve the data from the internet.")
            print(f"Data from year {year} downloaded and saved.")
        return

    def export_downloaded_years(self, array_of_years=None, params_to_keep=None,
                                file_path='./data/NCEI/ghcn/daily/',
                                file_path_dest="./data/NCEI/modified/daily/"):
        """
        This imports the specified years from the specified source path modifies it and exports them as a csv file in the specified destination directory

        :param array_of_years: the years to load and modify
        :param params_to_keep: the list of parameters to keep
        :param file_path: the directory where the source csv.gz files can be found
        :param file_path_dest: the directory where the modified csv files should be saved
        :return:
        """

        if params_to_keep is None:
            params_to_keep = ["TMIN", "TMAX", "PRCP", "SNOW"]
        if array_of_years is None:
            array_of_years = [1994]

        columns = ["stationcode", "datelabel", "param", "value", "mflag", "qflag", "sflag", "time"]

        for year in array_of_years:
            print(f"...Year {year} processing...")
            try:
                print(f"Loading data from year {year}")
                file_path_source = f"{file_path}{year}.csv.gz"
                df = pd.read_csv(file_path_source, names=columns, compression="gzip")
                print(f"Data from year {year} loaded.")

                # Convert time to int
                df['time'] = df['time'].fillna(1200)
                df['time'] = df['time'].apply(lambda x: int(Decimal(x)))
                # Convert values to float
                df = df.astype({"value": "float32"})

                # Cleanse dataset: keep only the parameters of interest, i.e. TMIN, TMAX, PRCP, SNOW
                df = df[df["param"].isin(params_to_keep)]

                scaling_factors = {"TMIN": 0.1, "TMAX": 0.1, "PRCP": 0.1}

                for k, v in scaling_factors.items():
                    df.loc[df["param"] == k, "value"] *= v

                df = df.fillna('')

                os.makedirs(file_path_dest, exist_ok=True)
                df.to_csv(f"{file_path_dest}/modified_{year}.csv", index=True, header=False)
                print(f"Export of year {year} finished.")
            except Exception as error:
                print(f"Error: {error}")
        return