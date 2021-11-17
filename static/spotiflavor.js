const $body = $('body');

BASE_URL = 'http://127.0.0.1:5000/api';
// BASE_URL = 'https://spotiflavor.herokuapp.com/api';

const playlistTracks = [];
let currentPlaylist;
let curr_audio_features = [];
let offset = 0;

// Create the HTML to display the playlist tracks
const makePlaylistHTML = (name, id) => {
	return `<li data-id=${id}> ${name} <button class="del-track btn btn-warning btn-sm">X</button></li>`;
};

// Update the playlist display
const updatePlaylist = () => {
	console.debug('updatePlaylist');

	let newTrack = $(makePlaylistHTML(track.name, track.id));
	$('#playList').append(newTrack);

	for (let track of playlistTracks) {
		let newTrack = $(makePlaylistHTML(track.name, track.id));
		$('#playList').append(newTrack);
	}
};

// Create the HTML for displaying the audio features
const makeFeaturesHTML = async (id) => {
	console.debug('makeFeaturesHTML');

	const features = await axios.get(`${BASE_URL}/tracks/${id}`);

	return `
    
    <div class="row">
      <div class="col-12">
        <h4>Audio Features</h4>
        <p>Name: ${features.data.name}<br>
        Album: ${features.data.album}</p>
      </div>
    
      <div class="col-6">
        Release Year: ${features.data.release_year}<br>
        Duration: ${features.data.duration}</p>

        <p>Popularity: ${features.data.popularity}<br>
        Acousticness: ${features.data.acousticness} (0-1)<br>
        Speechiness: ${features.data.speechiness} (0-1)<br>
        Instrumentalness: ${features.data.instrumentalness} (0-1)<br>
        Liveness: ${features.data.liveness} (0-1)</p>

      </div>
      <div class="col-6">
        <p>Key: ${features.data.key} ${features.data.mode}<br>
        Beats per measure: ${features.data.time_signature}</p>

        <p>Danceability: ${features.data.danceability} (0-1)<br>
        Energy: ${features.data.energy} (0-1)<br>
        Avg Tempo: ${features.data.tempo}<br>
        Loudness: ${features.data.loudness} avg db<br>
        Valence: ${features.data.valence} (0-1)</p>
    </div>
    `;
};

// Display audio features for track when mouse hovers over iframe
const showAudioFeatures = async (e) => {
	console.debug('showAudioFeatures');

	const $p = $(e.target).closest('p');
	const id = $p.data('id');
	let features = await makeFeaturesHTML(id);
	$('#audio-features').html(features);
};

// Add track to playlist locally
const handleAdd = async (e) => {
	console.debug('handleAdd');

	const $track = $(e.target).closest('p');
	const id = $track.data('id');
	const spotId = $track.data('spotid');
	const name = $track.data('name');

	playlistTracks.push({ name: name, id: id });
	let newTrack = $(makePlaylistHTML(name, id));
	$('#playList').append(newTrack);

	payload = { id: [ id ] };

	if (currentPlaylist) {
		// send new track to database
		const res = await axios.post(
			`${BASE_URL}/playlists/${currentPlaylist}/tracks`,
			payload
		);
		console.debug(res.data.playlist_id);
	}
};

// Delete track db and update display
const deleteTrack = async (e) => {
	console.debug('deleteTrack');

	const $track = $(e.target).closest('li');
	const id = $track.data('id');

	payload = { id: [ id ] };

	if (currentPlaylist) {
		const res = await axios.patch(
			`${BASE_URL}/playlists/${currentPlaylist}/tracks`,
			payload
		);
		console.log(res.data.deleted);
	}
	$track.remove();
};

// Create playist if it doesn't exist or update playlist info if it does
const createPlaylist = async (e) => {
	console.debug('createPlaylist');

	const $form = $('#form');
	const $username = $form.data('username');
	const name = $('#name').val();
	const description = $('#description').val();
	console.log('New Playlist', name, description);

	if (currentPlaylist) {
		console.debug('Playlist exists');

		playlist_payload = { name, description };
		const res = await axios.put(
			`${BASE_URL}/playlists/${currentPlaylist}`,
			playlist_payload
		);
	} else {
		console.debug('New Playlist');

		const playlist_payload = { name, description, playlistTracks };
		const res = await axios.post(
			`${BASE_URL}/users/${$username}/playlists`,
			playlist_payload
		);

		currentPlaylist = res.data.playlist_id;
		$('#createPlaylist').html('Update Playlist');
	}
};

// Create HTML for display of track iframes
const makeTracksHTML = async (tracks) => {
	console.debug('makeTracksHTML');

	html =
		'<p><button id="previous" class="btn btn-info">Previous Page</button> <button id="next" class="btn btn-info">Next Page</button></p>';
	for (const track of tracks) {
		html += `<p data-name="${track.name}" data-id="${track.id}" data-spotid="${track.spotify_track_id}">
        <iframe src="https://open.spotify.com/embed/track/${track.spotify_track_id}" width="380"
        height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe><button
        class="btn btn-info btn-sm addToPlaylist">Add</button>
        </p>`;
	}
	return html;
};

// Display the next page of Spotify tracks
const nextPage = async () => {
	console.debug('nextPage');

	offset += 10;

	const res = await axios.get(`${BASE_URL}/me/tracks?offset=${offset}`);
	const tracks = res.data.track_dicts;
	const html = await makeTracksHTML(tracks);
	$('#tracks').html(html);
};

// Display the previous page of tracks
const prevPage = async () => {
	console.debug('prevPage');

	offset -= 10;
	if (offset < 0) offset = 0;

	const res = await axios.get(`${BASE_URL}/me/tracks?offset=${offset}`);
	const tracks = res.data.track_dicts;
	const html = await makeTracksHTML(tracks);
	$('#tracks').html(html);
};

// Sync the local playlist with Spotify (update any track changes)
const spotSync = async (e) => {
	console.debug('spotSync');

	const $playlist = $(e.target).closest('li');
	const id = $playlist.data('id');
	const playlistId = $playlist.data('spotId');

	const res = await axios.post(`${BASE_URL}/spotify/${id}/playlists`);
	if (res.error) {
		console.log(res.message);
	}
};

// Display an iframe of the selected Spotify playlist
const showSpotPlaylist = async (e) => {
	console.debug('showSpotPlaylist');

	const $playlist = $(e.target).closest('li');
	const id = $playlist.data('spot-id');

	html = `
    <iframe src="https://open.spotify.com/embed/playlist/${id}" width="300" height="650" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
    `;
	$('#spotPlaylist').html(html);
};

// Display a list of iframes for the selected local playlist
const showPlaylist = async (e) => {
	console.debug('showPlaylist');

	const $playlist = $(e.target).closest('li');
	const id = $playlist.data('id');

	tracks = await axios.get(`${BASE_URL}/playlists/${id}/tracks`);

	playlist_tracks = '';
	for (let track of tracks.data.tracks) {
		playlist_tracks += `<p>
        <iframe src="https://open.spotify.com/embed/track/${track}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
        </p>`;
	}
	$('#playlistTracks').html(playlist_tracks);
};

// List of available endpoints
// create playlist: POST /users/<username>/playlists
// update playlist details: PUT /playlists/<playlist_id>
// get playlist: GET /playlists/<playlist_id>
// get playlist items: GET /playlists/<playlist_id>/tracks
// add items to playlist: POST /playlists/<playlist_id>/tracks
// update playlist items: PUT /playlists/<playlist_id>/tracks
// remove playlist tracks: DELETE /playlists/<playlist_id>/tracks
// get current user's playlists: GET /me/playlists
// get user's playlists: GET /users/<username>/playlists
// get track's audio features: GET /tracks/<track_id>
// create new spotify playlist: POST /spotify/<int:id>/playlists

$body.on('click', '.addToPlaylist', handleAdd);
$body.on('click', '#createPlaylist', createPlaylist);
$body.on('click', '.del-track', deleteTrack);
$body.on('click', '#next', nextPage);
$body.on('click', '#previous', prevPage);
$body.on('click', '.spotSync', spotSync);
$body.on('click', '.showSpotPlaylist', showSpotPlaylist);
$body.on('click', '.showList', showPlaylist);
$('iframe').hover(showAudioFeatures);
