# Tuttitracks

A web app that allows a user to interact with their Spotify account, search for tracks and track info, and create playlists.

## App Features

- Search for and view audio tracks (By album name, track name, artist name, genre, and year)
- View audio track feature information (This is track metadata that the standard Spotify app does not access), including:

  - Average Tempo (in BPM, beats per minute)
  - Beats per Measure (Time Signature)
  - Key Signature
  - Popularity
  - Acousticness
  - Danceability
  - Speechiness
  - Intrumentalness
  - Liveness
  - Energy
  - Loudness
  - Valence

- Create and edit Spotify playlists
- Playlists can be created and edited locally and uploaded and synched to your Spotify account.
- Playlists can be downloaded from a Spotify account, edited, and played and then synched to the Spotify account.
- View the Spotify user's liked audio tracks
- View the Spotify user's top played audio tracks
- Play audio tracks and playlists

Note: A Spotify Account (either a free or a premium account) is required in order to use the Tuttitracks web app.

---

## App Implementation Details

- PostgreSQL Database of users, tracks, features, playlists, artists, albums, and genres
- Implemented using Flask 2.2.3
- Implemented using Python 3.11.2
- The front-end is implemented with Ajax and JQuery
- RESTful database API
- The app implements OAuth for authorization with Spotify
- Unit-testing test suite
- Deployed to Heroku

## Tuttitracks is deployed on Heroku

[https://tuttitracks.herokuapp.com](Tuttitracks App)

## Usage

In order to use the app, the user must have a Spotify account. Any account, free or premium will work.  
Per Spotify, currently the app access to Spotify's backend is in development mode. Users of the app must be added by myself to the approved list of email addresses (with a Spotify account) to be able to query Spotify's database. Until Spotify grants general usage access to this app, anyone wanting to use the web app must contact me with the email address that is connected to a user's Spotify account so that I can manually add them. I have applied to Spotify to change this status and am waiting for their approval.

### User Interface

There are 4 main pages:

#### Search

The search page will allow you to enter artist, track name, album name, genre, year, or any combination to search for tracks.  
The search will redirect you to a page that will show you the search criteria you entered and display a list of matching tracks.  
30 second clips of the tracks can be played.
Mousing over the tracks will display the audio features for the track .
Each track has an add button that will add the track to playlist.
Playlist tracks may be dragged and dropped to change their order.  
The playlist can be named and given a description.

#### Liked Tracks

The saved tracks page will display the saved or "liked" tracks that a user has in their Spotify account.  
The tracks are displayed in pages of 25 and can be browsed with the Previous and Next Page buttons.  
30 second clips of the tracks can be played.  
Mousing over the tracks will display the audio features for the track.
Each track has an add button that will add the track to playlist.
Playlist tracks may be dragged and dropped to change their order.
The playlist can be named and given a description.

#### Top Tracks

The saved tracks page will display the tracks that a user has played most in the past from their Spotify account.  
The tracks are displayed in pages of 25 and can be browsed with the Previous and Next Page buttons.  
30 second clips of the tracks can be played.  
Mousing over the tracks will display the audio features for the track.
Each track has an add button that will add the track to playlist.
Playlist tracks may be dragged and dropped to change their order.  
The playlist can be named and given a description.

#### Playlists

The playlist page displays a list of all Spotify playlists displayed in pages of 25 that can be paged through.  
Clicking the show button next to each Spotify playlist will display the tracks of the playlist in a playable iframe.  
A list of the playlists created using this app are also displayed.
Clicking **Show** will display a list of tracks from which 30 second clips can be played.  
Clicking the Send button will upload the playlist to Spotify.  
Clicking the Sync button will sync any track changes with the playlist on the Spotify server.

---

## Getting Stared

Clone the repo by running

```bash
git clone https://github.com/Keparoo/Tuttitracks.git
```

### Key Dependencies

- [Python 3.11.2](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python) This project was developed using Python 3.8.5, upgraded to Python 3.8.10, and currently Python 3.11.2. The project will not run with versions of Python below 3.6.
- [Flask 2.2.3](https://flask.pocoo.org/) handles requests and responses.
- [FlaskSQLAlchemy 3.0.3](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/) is the Python SQL toolkit and ORM used to handle PostgreSQL database.
- [Flask-Bcrypt 1.01](https://github.com/maxcountryman/flask-bcrypt) handles password hashing.
- [psycopg2-binary 2.9.5](https://www.psycopg.org/) is the PostgresQL database adapter.
- [requests 2.28.2](https://requests.readthedocs.io/en/latest/) handles HTTP requests.
- [python-dotenv 1.0.0](https://github.com/theskumar/python-dotenv) handles environment variable imports.
- [Flask-WTF 1.1.1](https://github.com/wtforms/flask-wtf/) Handles forms and validation in Flask.
- [email_validator 1.1.1](https://github.com/JoshData/python-email-validator) handles email validation for Flask-WTF.

- [PostgreSQL](https://www.postgresql.org/docs/) is the object-relational SQL database system used.

- [Flask-Migrate](https://flask-cors.readthedocs.io/en/latest/) is used to handle SQLAlchemy database migrations for Flask applications using Alembic. The database operations are made available through the Flask command-line interface.

- [Unittest](https://docs.python.org/3/library/unittest.html) is the Python testing framework used for unit testing.
- [Flask-Debug-Toolbar 0.13.1](https://github.com/pallets-eco/flask-debugtoolbar) is a debugging tool used during development
- [gunicorn 20.1.0](https://gunicorn.org/) is used to deploy to Heroku

#### Virtual Enviornment

It is recommended to work within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/).

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
. venv/bin/activate
```

#### Installing Python Dependencies

Once the virtual environment is setup and running, install the required dependencies by navigating to the project directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages in the `requirements.txt` file.

---

## Database Setup

The project uses **PostgreSQL** databases.

- Create two databases: One for **testing** and one for **development**

```bash
createdb <database_name>
```

- Generate database tables from the migration files included by executing:
  `python manage.py db upgrade`
- Add starter data by executing:
  `python manage.py seed`

- Set the `DATABASE_URL` and `TEST_DATABASE_URL` in `.env` file to match the names of your development and testing databases.

- The schema for the database can be viewed visually in the tuttitracks-schema-design-3.4.pdf file

### The Postgres service must be running in order for the app to function

- To run the Postgres service on Linux:

```bash
sudo service Postgres start
```

- To stop the Postgres service on Linux:

```bash
sudo service Postgres stop
```

## Running the Server

Switch to the project directory and ensure that the virtual environment is running.

### To run the **development** server, execute

```bash
source setup.sh
flask run
```

---

## Environment Variables

Create a `.env` file matching the template provided in the `.env.example` file. All environmental variables must be populated with the appropriate `auth0` constants and `PostgreSQL` database URLs in order for the application to function.

In order to create a Spotify web app, visit [Spotify developer page](https://developer.spotify.com/). Log in and from the dashboard create a new app. Once this is done, the dashboard will provide you with a Client Id and Client Secret. These are necessary to run this code and must be placed in the .env file.  
From the developers dashboard, any redirect urls used in the auth.py file must be entered into the Spotify app created on the dashboard.

## Testing

A seed.py file is included that will drop and create tables in the database and seed it with test data in order to become familiar with the database schema. This data may also be used for unit testing.

For testing locally, stop the development server and reset the database.
The following resets the database and runs the test suite:

```bash
source setup_test.sh
```

## To return to development mode

```bash
source setup.sh
```

---

## Deployment

This project is deployed to [Heroku](https://heroku.com). To Deploy your own version:

- You must have Git installed and your project must be tracked in a repository
- Install Heroku locally: [https://devcenter.heroku.com/articles/heroku-cli](Heroku Dev Center)
- Create your heroku app:

```bash
heroku create <name_of_app>
```

- If project is has already been created, login to Heroku

```bash
heroku login
```

- Add `heroku` as a Git remote and push your project to `Heroku` (Change `main` to the name of the appropriate git brach if it differs, i.e. `master`). To find Heroku Git Url, from the project dashboard go to settings. It is found under App Information or from the command line:

```bash
git remote -v
```

```bash
git remote add heroku <heroku_git_url>
git push heroku main
```

- Create a postgres database in Heroku:

```bash
heroku addons:create heroku-postgresql:hobby-dev --app <name_of_app>
```

- go to settings on the [Heroku dashboard](https://dashboard.heroku.com/) for the app you've built and click on `Show Environment Variables`. You will need to set environmental variables for each variable found in the `.env.example` file.

- Once your app is deployed, run migrations by running:

```bash
heroku run python manage.py db upgrade --app <name_of_app>
```

- To see the Heroku logs for debugging:

```bash
heroku logs --tail
```

- To reset the Heroku database:

```bash
heroku run python manage.py db downgrade --app <name_of_app>
heroku run python manage.py db upgrade --app <name_of_app>
heroku run python manage.py seed --app <name_of_app>
```

- To solve an error code of H14 or no dynos running on Heroku:

```bash
heroku ps:scale web=1
```

---

### Author

Kep Kaeppeler is the author of this project, test suite, and all documentation. © 2023
