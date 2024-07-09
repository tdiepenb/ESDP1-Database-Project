# ESDP1-Database-Project

Rename .env-example to .env if you want to use it :))

To Run the database cd into the nceiDatabase folder using `cd ./nceiDatabase`

Then run `docker-compose up` and if it is the first time starting the database add the `--build` flag to the end of the
command.

## How to check the databases

docker exec -it esdp-db-1 bash

psql -U myuser -d mydatabase -h localhost

SELECT COUNT(\*) FROM Climate1952;
