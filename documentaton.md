## Documentation

This is a documentation of what was done to create this project.

Table of Content:

1. Data exploration
2. Basic Database Setup
3. Creation of Station Models in the Database

Description of Steps:

## 1. Data exploration

Initially we explored the available data using the stations.ipynb and weather.ipynb files.

## 2. Basic Database Setup

To get started on the Database we initially set up an empty Postgresql Database using Django.
We directly dockerized the Database.
To do this we executed the following steps:

- Install Django using pip
- Start a Django project using the command `django-admin startproject nceiDatabase`
- cd into the nceiDatabase folder
- create a Dockerfile with the following code

```
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container
COPY requirements.txt /code/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /code/
COPY . /code/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV DJANGO_SETTINGS_MODULE=nceiDatabase.settings

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

```

- create a requirements.txt file that includes the code to install django and postgres client in the docker container

```
Django>=3.2,<4.0
psycopg2-binary
```

- edit the /nceiDatabase/nceiDatabase/settings.py file to use Postgresql

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydatabase',
        'USER': 'myuser',
        'PASSWORD': 'mypassword',
        'HOST': 'db',
        'PORT': 5432,
    }
}
```

- using the command `python manage.py startapp database` we then create a new app called database which we can find
  under ./nceiDatabase/database
- within the ./nceiDatabase/nceiDatabase/settings.py we then added `database` to the list of installed apps
- in the ./nceiDatabase folder createe a docker-compose.yml file that creates a container with two services (db and
  web). For the db the docker-compose pulls the official postgres docker image

```
version: '3.8'

services:
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydatabase
      POSTGRES_USER: myuser
      POSTGRES_PASSWORD: mypassword

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_data:

```

- we can then use `docker-compose up --build` to initially build the services and container.
- using the command `docker-compose exec web python manage.py migrate` we then tell django to create the migrations that
  create the initial postgreSQL tables in the database.

## 3. Creation of Station Models in the Database

To create the model we added a Station class to the ./nceiDatabase/database/models.py file.
For most of the attributes we added CharFields with an appropriate max_length parameter. For longitude, latitude and
elevation we used DecimalFields as they are encoded with a fixed amount of decimal places.

After creating the model we used the commands `docker-compose exec web python manage.py makemigrations` to create a
migration and `docker-compose exec web python manage.py migrat` to apply the migration to our database.

