# Spotiflavor
This is a web app that allows you to interact with a Spotify account to search for tracks, view saved (liked) tracks, see audio feature information like key, time-signature, tempo etc., and create and edit playlists that can be uploaded to a Spotify account.

Note: in order to use this web app a Spotify account is required: either free or paid.

---

## Features
- Postgresql Database of users, tracks, features, playlists, artists, albums and genres
- RESTful API to interact with the database
- This app manages
- Unit testing test suite
- Deployed to Heroku

## Spotiflavor is deployed on Heroku
https://spotiflavor.herokuapp.com/

## Usage
In order to user the app, the user must sign up for a Spotify account. Any account, free or premium will work.  
There are 3 main pages:

### Search
The search page will allow you to enter artist, track name, album name genre or year or any combination to search for tracks  
The search will redirect you to a page that will show you the search criteria you entered and display a list of matching tracks.  
30 second clips of the tracks can be played
Mousing over the tracks will display the audio features for the track  
Each track has an add button that will add the track to playlist  
The playlist can be named and given a description  

### Saved Tracks
The saved tracks page will display the saved or "liked" tracks that a user has in their Spotify account.  
The tracks are displayed in pages of 25 and can be browsed with the Previous and Next Page buttons  
30 second clips of the tracks can be played  
Mousing over the tracks will display the audio features for the track 
Each track has an add button that will add the track to playlist  
The playlist can be named and given a description  

### Playlists
The playlist page displays a list of all Spotify playlists displayed in pages of 25 that can be paged through  
Clicking the show button next to each Spotify playlist will display the tracks of the playlist in a playable iframe  
A list of the playlists created using this app are also displayed
Clicking Show will display a list of tracks from which 30 second clips can be played  
Clicking the Send button will upload the playlist to Spotify  
Clicking the Sync button will sync any track changes to the playlist with the Spotify server

## Testing

There is a testing suite with this app. To run tests:

```bash
python -m unittest
```
