# Casting Agency Backend

## Motivation
The following project was done to fulfill the capstone project requirements for Udacity's Full Stack Nanodegree Course.

## Overview
The following project models the backend of a web application for a Casting Agency Company. The Casting Agency API models a company that is responsible for creating movies, and managing and assigning actors to those movies. The backend streamlines this process buy providing API endpoints to create movies and actors, updates their respective information, and to delete selected resources.

### Hosting
This web application is currently hosted at https://casting-agency-pib.herokuapp.com/ . As of yet, there is no front-end for this application. To access endpoints, it is recommend that users utilize curl requests or Postman. Authentication tokens for the various roles needed to access the API's endpoints can be found in setup.sh. If the file is not included (likely because it is listed in .gitignore) or the tokens are expired, feel free to reach out to the developer (email: pibcrib@gmail.com).

## Main Files: Project Structure
```sh
    ├── README.md
    ├── Procfile  *** configuration for Heroku build
    ├── requirements.txt  *** python dependencies
    ├── manage.py *** script to handle Heroku database migrations
    ├── migrations *** migrations folder for manage.py
    └── backend
        └── src
            ├── __init__.py
            ├── app.py  *** main driver of api
            ├── test_app.py *** unittests for api endpoints
            ├── auth
            │   ├── __init__.py
            │   └── auth.py *** module for authenticating AUTH0 tokens
            └── database
               ├── __init__.py
               ├── models.py *** module script for creating database schema
               └── test_database_setup.py *** holds dummy data for initializing database
```
## Roles & Permissions
The Casting Agency Backend uses RBAC Authorization to access its endpoints.

#### Roles
There are 3 distinct Roles for this API:

  (1) Assistant Director: Allowed to access a list of all actors and/or movies i, as well as their information.

  (2) Casting Director: Assistant Director  + permission to add/delete actors, and update actors/movies.

  (3) Executive Producer: Casting Director +  permission to add/delete movies.

#### Permissions
To facilitate the above jobs, and the tasks of the Casting Agency, the following permissions are assigned to each role.

```sh
Assistant Director:
  (1) get:actors
  (2) get:movies

Casting Director:
  assistant director permissions +
  (3) post:actors
  (4) delete:actors
  (5) patch:actors
  (6) patch:movies

Executive Producer:
  casting director permissions +
  (7) post:movies
  (8) delete:movies

In the next section, the documentation of each API endpoint specifies specifically which permission(s) is needed.
```
## API Endpoints

```js
GET '/movies'
- Fetches a list of all movies in the database.
- Permissions Needed: 'get:movies'
- Request Arguments: NONE
- Returns: Object with a list of all movies and their attributes, the total number of movies, and a success flag.
    {
          "success": true,
          "movies": [
              {
                "id": 1,
                "title": 'Amor en El Tiempo de Corona',
                "release": 'Sat, 25 Dec 2021 00:00:00 GMT'
              }, ...
          ],
          "total_num_movies": 12
    }
```
```js
GET '/actors'
- Fetches a list of all actors in the database.
- Permissions Needed: 'get:actors'
- Request Arguments: NONE
- Returns: Object with a list of all actors and their attributes, the total number of actors, and a success flag.
    {
          "success": true,
          "actors": [
              {
                  "age": 36,
                  "current_movie": "Amor en El Tiempo De Corona",
                  "current_movie_id": 1,
                  "gender": "Male",
                  "id": 1,
                  "name": "John Smith"
              }, ...
          ],
          "total_num_actors": 30
    }
```
```js
GET '/movies/${movie_id}/actors'
- Fetches a list of actors for a given movie.
- Permissions Needed: 'get:actors'
- Request Arguments: Integer corresponding to integer ID of a movie in the database.
- Returns: Object with a list of actors for the given movie, the number of actors for the movie, the current movie, and a success flag.
    {
          "actors": [
              {
                  "age": 36,
                  "current_movie": "Amor en El Tiempo De Corona",
                  "current_movie_id": 1,
                  "gender": "Male",
                  "id": 2,
                  "name": "John Smith"
              }, ...
          ],
          "current_movie": {
              "id": 1,
              "release": "Sat, 25 Dec 2021 00:00:00 GMT",
              "title": "Amor en El Tiempo De Corona"
              },
          "num_actors": 2,
          "success": true
    }
```
```js
POST '/movies'
- Adds a new movie to the database
- Permissions Needed: 'post:movies'
- Request Arguments: NONE
- Request Body: Object with values for the movie title and release date.
    {
          "release": "Sat, 01 Jan 2022 00:00:00 GMT",
          "title": "So it Goes"
    }
- Returns: Object indicating creation was successful and the id of the created movie.
    {
          "success": true
          "new_movie_id": 2
    }
```
```js
POST '/actors'
- Adds a new actor to the database
- Permissions Needed: 'post:actors'
- Request Arguments: NONE
- Request Body: Object with values for the actors name, age, and gender, and the id of the movie the actor is currently assigned to if applicable.
    {
          "name": "Jennifer Lawrence"
          "age": 31,
          "gender": "Female",
          "movie_id": 2,
    }
- Returns: Object indicating creation was successful and the id of the added actor.
    {
          "success": true
          "new_actor_id": 3
    }
```
```js
PATCH '/movies/${movie_id}'
- Updates select movie in the database
- Permissions Needed: 'patch:movies'
- Request Arguments: Integer value for movie_id corresping to ID of movie in database
- Request Body: Object with new values for  movie title and/or release date.
    **Following request body example is for request sent to '/movies/1'
    {
          "title": "A Day in the Life of a Programmer"
    }
- Returns: Object indicating update was successful and the attributes or the updated movie.
    {
          "success": true
          "updated_movie": {
              "title": "A Day in the Life of a Programmer",
              "release": "Sat, 25 Dec 2021 00:00:00 GMT"
          }
    }
```
```js
PATCH '/actors/${actor_id}'
- Updates select actor in the database
- Permissions Needed: 'patch:actors'
- Request Arguments: Integer value for actor_id corresping to ID of actor in database
- Request Body: Object with values for the actors name, age, and/or gender, and/or the id of the movie the actor is being reassigned to if applicable.
    **Following request body example is for request sent to '/actors/3'
    {
          "movie_id": 1,
    }
- Returns: Object indicating creation was successful and the attributes of the update actor.
    {
          "success": true
          "updated_actor": {
              "age": 31,
              "current_movie": "A Day in the Life of a Programmer",
              "movie_id": 1,
              "gender": "Female",
              "id": 2,
              "name": "Jennifer Lawrence"
          }
    }
```
```js
DELETE '/movies/${movie_id}'
- Deletes select movie from database, and reassigns associated actors to no movie.
- Permissions Needed: 'delete:movies'
- Request Argument: Integer value for movie_id corresponding to the ID of a movie in the database
- Returns: Object indicating the deletion was successful and the id of the deleted movie
    {
          "success": true
          "deleted_movie_id": 4
    }
```
```js
DELETE '/actors/${actor_id}'
- Deletes select actor from database
- Permissions Needed: 'delete:actors'
- Request Argument: Integer value for actor_id corresponding to the ID of an actor in the database
- Returns: Object indicating the deletion was successful and the id of the deleted actor
    {
          "success": true
          "deleted_actor_id": 3
    }
```

## Instructions for Local Development

### Installing Dependencies
#### Python 3.9.7
The application's backend was written exclusively in Python, using Pythion 3.9.7 during development. It is recommend that this same Python version is used in development when testing or modifying the above project. Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual environment
When running application locally, it is recommend that a virtual environment is used to isolate the project's dependencies from other projects and your system's environment.

Instructions for setting up a virtual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies
Once you have a virtual environment setup and running (or you're feeling bold and ignored that step), install dependencies by navigating to the root folder of this project directory, `/Capstone`, and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages listed in the `requirements.txt` file.

###### Key Python Dependencies
- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) and [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) are libraries used to handle the lightweight Postgres database for the API.

- [jose](https://python-jose.readthedocs.io/en/latest/) JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTS, and utilized in the project to authenticate users before use of endpoints.  

### Setting Up Local Database
#### PostgreSQL
The project is currently built to interface with a PostgreSQL database by default. Though databases using other SQL dialects can be used, it is recommend that you use a PostgreSQL database in development and production. Instructions for downloading and getting started with PostgreSQL can be found in the [PostgreSQL docs](https://www.postgresql.org/docs/).


#### Integrating SQL Database
By default, in `/backend/database/models.py` line 10, the database path for API is set to `postgres://postgres@localhost:5432/castingagency`. This value however can be overwritten by setting an environment variable `DATABASE_URL` with the value of your respective uri of your sql databse.

Once you have created a database for the application, PostgreSQL or otherwise, and before you run the server, it is highly recommend that you open a terminal session and set a variable `DATABASE_URL` equal to the uri of your database, rather than modify the code in `models.py`. THE VARIABLE MUST HAVE THIS EXACT NAME IN ORDER TO FUNCTION!

### Running Development Server
From within the `./src` directory first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_DEBUG=true;
export DATABASE_URL=URI;
```
where URI is equal to the value of you local database's path (See `Setting Up Local Database - Integrating SQL Database` section for more details.)

If running the server for the first time, you can uncomment line 17 in `backend/src/app.py` before executing the script to populate the database with dummy data. Comment out this line again after the first time you run the server.

To run the server, from within `./src` execute:

```bash
python app.py
```


## Instruction for Running Tests
Unit tests have been created to test the API's key endpoints, as well as any errors, in `/backend/src/test_app.py`. To execute the tests, it is first necessary to create a separate test database. Once you have done so, open a terminal session and run:

```bash
export DATABASE_URL_TEST=TEST_URI;
export ASSITANT_TOKEN=token1
export DIRECTOR_TOKEN=token2
export PRODUCER_TOKEN=token3
```
where TEST_URI is equal to the value of your test databases' path, and token's 1 - 3 are respectively the AUTH0 tokens for the Assistant Director, Casting Director, and Executive Producer roles respectively. These tokens can be found in `setup.sh` or requested from the developer.

Once the above environment variables have been set, from within the `/backend/src` directory, run the following:

```bash
python test_app.py
```
