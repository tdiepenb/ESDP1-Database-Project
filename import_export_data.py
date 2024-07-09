import pandas as pd
import os
import requests

def download_years(years =[], file_path="./data/climate/script"):
    for year in years:
        print(f"...Downloading data from year {year}....")
        url = f"https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_year/{year}.csv.gz"
        response = requests.get(url)
        if response.ok:
            filename = url.rsplit('/', 1)[1]
            print(f"data downloaded. Will be saved as {filename}")
            directory_path = file_path
            os.makedirs(directory_path, exist_ok=True)
            with open(f"{file_path}/{filename}", "wb") as f:
                f.write(response.content)
        else:
            print("An error occured while trying to retrieve the data from the internet.")
        print(f"Data from year {year} downloaded and saved.")


def export_downloaded_years(years = [], file_path_source ='./data/climate/1949.csv.gz', file_path_dest="./data/export/climate"):
    try:
        for year in years: 
            print(f"Year {year} processing.")

            columns = ["stationcode", "datelabel", "param", "value", "mflag", "qflag", "sflag", "time"]
            
            df = pd.read_csv(file_path_source, names=columns, compression="gzip")

            # convert values to float
            df = df.astype({"value": "float32"})            

            # cleanse dataset: keep only the parameters of interest, i.e. TMIN, TMAX, PRCP, SNOW
            keep = ["TMIN", "TMAX", "PRCP", "SNOW"]

            df = df[df["param"].isin(keep)]

            scaling_factors = {"TMIN": 0.1, "TMAX": 0.1, "PRCP": 0.1}

            for k, v in scaling_factors.items():
                df.loc[df["param"]==k,"value"] *= v

            # # df = df.replace(np.nan, '', regex=True)
            # df.replace(['None', 'nan'], np.nan, inplace=True)
            df = df.fillna('')

            directory_path = file_path_dest
            os.makedirs(directory_path, exist_ok=True)
            df.to_csv(f"{file_path_dest}/modified_{year}.csv", index=False, header=False)

            

    except Exception as error:
        print(f"Error: {error}")
    
    finally:
        print(f"Export of year {year} finished.")
        
    
    
