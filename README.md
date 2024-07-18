# ESDP1-Database-Project

## Basic information
- Team: Tilmann Diepenbruck, Fabian Klug
- University project for Earth systems data processing
- Student project for University of Cologne

## Project Overview

This project aims to transform daily climate summaries into a fully operational database system using PostgreSQL. It
includes functionalities for downloading data, ingesting it into the database, managing station information, performing
data analysis, and optionally, creating a web service for data visualization.

## Data descrption

The Global Historical Climatology Network - Daily (GHCN-Daily) dataset integrates daily climate observations from
approximately 30 different data sources. Version 3 was released in September 2012 with the addition of data from two
additional station networks. Changes to the processing system associated with the version 3 release also allowed for
updates to occur 7 days a week rather than only on most weekdays. Version 3 contains station-based measurements from
well over 90,000 land-based stations worldwide, about two thirds of which are for precipitation measurement only. Other
meteorological elements include, but are not limited to, daily maximum and minimum temperature, temperature at the time
of observation, snowfall and snow depth. Over 25,000 stations are regularly updated with observations from within
roughly the last month. The dataset is also routinely reconstructed (usually every week) from its roughly 30 data
sources to ensure that GHCN-Daily is generally in sync with its growing list of constituent sources. During this
process, quality assurance checks are applied to the full dataset. Where possible, GHCN-Daily station data are also
updated daily from a variety of data streams. Station values for each daily update also undergo a suite of quality
checks.
NOAA National Climatic Data Center. http://doi.org/10.7289/V5D21VHZ [17.07.2024]

## Project Goals and progress

- The Presentation.ipynb file contains a rundown demo for the task [here](./Presentation.ipynb)

1. **Data Acquisition and Ingestion:** [✔]

    - Download daily climate summaries for at least 10 years and load them into a PostgreSQL database.
    - Automate data download and ingestion processes.

2. **Database Structure:** [✔]

    - Define the database schema to store climate data and station metadata efficiently.

3. **Functionality:** [✔]

    - Develop Python functions to query the database based on user-specified station and parameters.
    - Implement basic data analysis capabilities such as plotting graphs based on user inputs.

4. **Optional Web Service:** [✖]
    - Create a web-based frontend to interact with the database, allowing users to select stations and parameters and
      visualize data.

## Implementation Details

### Docker Setup

- Utilize Docker for setting up the PostgreSQL database.
- Advantages of Docker include easy deployment, isolation of dependencies, and scalability.
- You can download Docker from here: https://www.docker.com/

### Project Modules

#### nceiDatabaseManager

- **Description:** Contains functions to manage interactions with the PostgreSQL database.
- **Features:**
    - Modular execution of database operations.
    - Database connection handling and query execution.

#### nceiDataManager

- **Description:** Handles data management tasks such as downloading, filtering, and exporting climate data.
- **Features:**
    - Automated data download with requests api.
    - Data filtering based on predefined criteria.

## Get started

### Prerequisite

- Python
    - Download python [here](https://www.python.org/downloads/)
- python packages
  ```bash
  pip install -r requirements.txt
  ```
- Docker
    - Download docker [here](https://docs.docker.com/get-docker/)

### Start project

- We configured a docker-compose.yml file which is used for controlling the docker container and its dependencies
- To start the docker container type for the first time
  ```bash
  docker-compose up -d --build # if not for the first time, just dismiss the --build flag
  ```

### Interact with project

- Create a new .ipynb file and insert the following code blocks
- setup user settings
  ```bash
  years_in_db = [1950, 1951, 1952, 1953, 1954, 2010, 2011, 2012, 2013, 2014]
  stations_file_path = "./data/stations/"
  modified_stations_file_path = "./data/stations/modifiedStations/"
  download_csv_file_path = "./data/NCEI/ghcn/daily/"
  modified_csv_file_path = "./data/NCEI/modified/daily/"
  db_name = "NCEIDatabase"
  db_user = "ESDP"
  db_password = "esdp1"
  debug_messages = False
  station_cols = ["id", "latitude", "longitude", "elevation", "state", "name", "gsn_flag", "hcn_crn_flag", "wmo_id"]
  weather_cols = ["id", "stationcode", "datelabel", "param", "value", "mflag", "qflag", "sflag", "time"]
  ```
- configure .env file

  ```bash
    #This command writes the db_name, db_user and db_password to an env file which is used by the docker-container during postgresql setup
    envVariables = {
        "DATABASE_NAME": db_name,
        "DATABASE_USER": db_user,
        "DATABASE_PASSWORD": db_password,
    }

    with open(".env", "w") as env_file:
        for key, value in envVariables.items():
            env_file.write(f"{key}={value}\n")

    print(".env file created successfully.")
  ```

- Impport the packages (adjust to the path of the modules - here
  /nceiDatabaseConnector/nceiDatabasePackage/nceiDataManager translates to the following)
  ```bash
  from nceiDatabaseConnector.nceiDatabasePackage.nceiDataManager import NCEIDataManager
  from nceiDatabaseConnector.nceiDatabasePackage.nceiDatabaseManager import NCEIDatabaseManager
  ```
- Create data and database instances

  ```bash
  ncei_db = NCEIDatabaseManager(db_name=db_name,
                       db_user=db_user,
                       db_password=db_password,
                       db_host="localhost",
                       db_port="5432",
                       debug_messages = False,
                       years_in_db=years_in_db)

  ncei_data = NCEIDataManager()
  ```

- Use the implemented functions

  ```bash
  ncei_db.create_stations_table()

  ncei_data.download_stations(file_path_dest=stations_file_path)
  ```

## Database Operations

### Checking Database Status

To interact with the PostgreSQL database using Docker:

1. Access the Docker container:

   ```bash
   docker exec -it esdp1-database-project-db-1 bash
   ```

2. Connect to database
   ```bash
   psql -U ESDP -d NCEIDatabase -h localhost
   ```
3. List all tables
   ```bash
   \dt
   ```
4. Check Climate table if it has values
   ```bash
   SELECT COUNT(*) AS count, stationcode
   FROM "Climate1952" ORDER BY count;
   ```
5. Check which stations has the most values
   ```bash
   SELECT COUNT(*) AS count, stationcode
   FROM "Climate1952"
   GROUP BY stationcode
   ORDER BY count
   DESC LIMIT 10;
   ```
6. Check which stations has lowest elevation
   ```bash
   SELECT * FROM "Station"
   WHERE elevation > -999
   ORDER BY elevation ASC
   LIMIT 10;
   ```
7. Check which stations has highest elevation
   ```bash
   SELECT * FROM "Station"
   WHERE elevation > -999
   ORDER BY elevation DESC
   LIMIT 10;
   ```
8. Check which stations has highest elevation
   ```bash
   SELECT COUNT(*) AS count, stationcode
   FROM "Climate1955" c
   LEFT JOIN "Station" s ON s.id = c.stationcode
   WHERE latitude < 0
   GROUP BY stationcode
   ORDER BY count DESC
   LIMIT 10;
   ```
