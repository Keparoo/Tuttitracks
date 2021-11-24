# Tuttitracks
This is a web app that allows you to interact with a Spotify account to search for tracks, view saved (liked) tracks, see audio feature information like key, time-signature, tempo etc., and create and edit playlists that can be uploaded to a Spotify account.

Note: in order to use this web app a Spotify account is required: either free or paid.

---

## Features
- Postgresql Database of users, tracks, features, playlists, artists, albums and genres
- Implemented using Flask 2.0
- Implemented using Python 3.8.10
- The front-end is implemented with Ajax and JQuery
- RESTful API to interact with the database
- The app handles authorization with Spotify
- Unit-testing test suite
- Deployed to Heroku

## Tuttitracks is deployed on Heroku
https://spotiflavor.herokuapp.com/

## Usage
In order to user the app, the user must sign up for a Spotify account. Any account, free or premium will work.  
There are 4 main pages:

### Search
The search page will allow you to enter artist, track name, album name genre or year or any combination to search for tracks  
The search will redirect you to a page that will show you the search criteria you entered and display a list of matching tracks.  
30 second clips of the tracks can be played
Mousing over the tracks will display the audio features for the track  
Each track has an add button that will add the track to playlist
Playlist tracks may be dragged and dropped to change their order  
The playlist can be named and given a description  

### Liked Tracks
The saved tracks page will display the saved or "liked" tracks that a user has in their Spotify account.  
The tracks are displayed in pages of 25 and can be browsed with the Previous and Next Page buttons  
30 second clips of the tracks can be played  
Mousing over the tracks will display the audio features for the track 
Each track has an add button that will add the track to playlist
Playlist tracks may be dragged and dropped to change their order  
The playlist can be named and given a description 

### Top Tracks
The saved tracks page will display the tracks that a user has played most in the past from their Spotify account.  
The tracks are displayed in pages of 25 and can be browsed with the Previous and Next Page buttons  
30 second clips of the tracks can be played  
Mousing over the tracks will display the audio features for the track 
Each track has an add button that will add the track to playlist
Playlist tracks may be dragged and dropped to change their order  
The playlist can be named and given a description 

### Playlists
The playlist page displays a list of all Spotify playlists displayed in pages of 25 that can be paged through  
Clicking the show button next to each Spotify playlist will display the tracks of the playlist in a playable iframe  
A list of the playlists created using this app are also displayed
Clicking Show will display a list of tracks from which 30 second clips can be played  
Clicking the Send button will upload the playlist to Spotify  
Clicking the Sync button will sync any track changes to the playlist with the Spotify server

## Getting Stared  

Clone the repo by running
```bash
git clone https://github.com/Keparoo/Spotiflavor.git
```
#### Key Dependencies
- [Python 3.8.10](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python) This project was developed using Python 3.8.5 and the project will not run with versions of Python below 3.6.
- [Flask 2.0](http://flask.pocoo.org/) handles requests and responses.
- [Flask-Migrate](https://flask-cors.readthedocs.io/en/latest/) is used to handle SQLAlchemy database migrations for Flask applications using Alembic. The database operations are made available through the Flask command-line interface.
- [PostgreSQL](https://www.postgresql.org/docs/) is the object-relational SQL database system used.
- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM used to handle PostgreSQL database.
- [Unittest](https://docs.python.org/3/library/unittest.html) is the Python testing framework used for unit testing.

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

## Running the Server
Switch to the project directory and ensure that the virtual environment is running.

#### To run the **development** server, execute:  

```bash
source setup.sh
flask run
```
--- 

## Environment Variables  
Create a `.env` file matching the template provided in the `.env.example` file. All environmental variables must be populated with the appropriate `auth0` constants and `PostgreSQL` database URLs in order for the application to function. 
## Testing

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
- Install Heroku locally: https://devcenter.heroku.com/articles/heroku-cli
- Create your heroku app:
```bash
heroku create <name_of_app>
```
- Add `heroku` as a Git remote and push your project to `Heroku` (Change `main` to the name of the appropriate git brach if it differs, i.e. `master`)
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
---

### Author
Kep Kaeppeler is the author of this project and all documentation.