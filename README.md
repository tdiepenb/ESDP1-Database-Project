# ESDP1-Database-Project

# Project description

# Task definition

# Implementation details

## Modules

1. nceiDatabaseManager
2. nceiDataManager

### nceiDatabaseManager

### nceiDataManager

Rename .env-example to .env if you want to use it :))

To Run the database cd into the nceiDatabase folder using `cd ./nceiDatabase`

Then run `docker-compose up` and if it is the first time starting the database add the `--build` flag to the end of the
command.

## How to check the databases

<code>docker exec -it esdp1-database-project-db-1 bash</code>
<code>psql -U ESDP -d NCEIDatabase -h localhost</code>
<code>SELECT COUNT(\*) FROM Climate1952;</code>
<code>SELECT COUNT(\*) AS count, stationcode FROM "Climate1950" WHERE stationcode LIKE '%GME%' GROUP BY stationcode ORDER BY count DESC;</code>
<code>SELECT COUNT(\*) AS count, stationcode FROM "Climate2010" WHERE stationcode LIKE '%GME%' GROUP BY stationcode ORDER BY count DESC;</code>
<code>SELECT \* FROM "Station" WHERE elevation > -999 ORDER BY elevation ASC LIMIT 10;</code>
<code>SELECT \* FROM "Station" WHERE elevation > -999 ORDER BY elevation DESC LIMIT 10;</code>
