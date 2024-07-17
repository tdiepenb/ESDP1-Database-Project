# ESDP1-Database-Project

## Project Overview

This project aims to transform daily climate summaries into a fully operational database system using PostgreSQL. It
includes functionalities for downloading data, ingesting it into the database, managing station information, performing
data analysis, and optionally, creating a web service for data visualization.

## Project Goals

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
