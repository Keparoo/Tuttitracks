const $body = $('body');

// BASE_URL = 'http://127.0.0.1:5000/api';
BASE_URL = 'https://spotiflavor.herokuapp.com/api';

let offset = 0;

// Create the HTML for the list of Spotify playlists
makeSpotPlaylists = async (playlists, total_spot_playlists) => {
	console.debug('makeSpotPlaylists');

	html = `<h3>Spotify Playlists ${total_spot_playlists}</h3>
    <p><button id="previous" class="btn btn-info">Previous Page</button> <button id="next" class="btn btn-info">Next Page</button></p><ul>`;

	for (const playlist of playlists) {
		html += `<li class="list-group-item" data-id="${playlist.id}" data-spot-id="${playlist.spotify_playlist_id}">${playlist.name} 
        <button class="btn btn-info btn-sm showSpotPlaylist float-right">Show</button></li>`;
	}
	html += '</ul>';
	return html;
};

// Display the next page of Spotify playlists
const nextPage = async () => {
	console.debug('nextPage');

	LIMIT = 20;
	offset += 10;

	const res = await axios.get(
		`${BASE_URL}/spotify/playlists?limit=${LIMIT}&offset=${offset}`
	);

	const playlists = res.data.spot_playlists;
	const total_spot_playlists = res.data.total_spot_playlists;
	const html = await makeSpotPlaylists(playlists, total_spot_playlists);
	$('#spotPlaylists').html(html);
};

// Display the previous page of Spotify playlists
const prevPage = async () => {
	console.debug('prevPage');

	LIMIT = 20;
	offset -= 10;
	if (offset < 0) offset = 0;

	const res = await axios.get(
		`${BASE_URL}/spotify/playlists?limit=${LIMIT}&offset=${offset}`
	);

	const playlists = res.data.spot_playlists;
	const total_spot_playlists = res.data.total_spot_playlists;
	const html = await makeSpotPlaylists(playlists, total_spot_playlists);
	$('#spotPlaylists').html(html);
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

$body.on('click', '#next', nextPage);
$body.on('click', '#previous', prevPage);
$body.on('click', '.spotSync', spotSync);
$body.on('click', '.showSpotPlaylist', showSpotPlaylist);
$body.on('click', '.showList', showPlaylist);
