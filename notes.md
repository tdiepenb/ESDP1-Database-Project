# Notes for ESDP1 Database Project

# What we want to do:

1. Download _daily_ summaries of at least 10 years and load them into the database (maybe create a script that automatically downloads the data from the ftp server and adds it to the database)
   - think about the database structure, which tables do we need, etc.
2. Load station table into Database
3. Create basic python functions that allows us to request data from the database and plot them
4. (optional) create a webbased frontend that can request the data and plot them

## Tech stack

- PostgreSQL for the Database
- Django as a Webframework to access the Database
- python or jupyter files to download data and load them into the database
- Docker for dockerization of the database (Backend) and Webpage (Frontend)

- (if time) Web Frontend to requst data and plot data from database (javascript basiert)

## Questions

- What is meant by testing routines?
- Does it matter which 10 years we choose for the initial database?
- how should we handle missing time?

## General project infos

Workload: around 40 hours per person
Half of the time should be preprocessing the data
Other half on some visualisation
Reusability, documentation and proper git workflow is very important
Presentation or paper.

CSV station data -> Database queries to compare visualisation, e.g. on map

## Project description:

I have expanded the csv code example in https://github.com/maschu09/esdp-file-formats - you could turn this into a real database (for example Postgres) and write some code to download all of the daily summaries, ingest them into the database, add a stations table, and perform some rudimentary analysis, where a user can select a station and the desired parameters, and you would extract the respective data from the database and plot it. And if you are really courageous, you can even turn this into a web service.

## Further notes:

- Database doesn’t have to be PosgresSQL (not even necessariliy SQL, maybe noSQL or compare two databases)
- Webservice to download data (maybe different file formats)
- Script to load data into the database
- At least 10 years maybe more of data should be included in the database (daily data)
- Maybe go through the CoreTrustSeal Requirements and check how far we could take our database. Also think about GO-FAIR when creating the database.
- Maybe Dockerize application: https://www.hifis.net/tutorial/2020/09/23/getting-started-with-docker-1.html
