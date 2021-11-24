const $body = $('body');

BASE_URL = '/api';

const LIMIT = 20;
let offset = 0; // current search page offset
let currentPlaylist; // id of current playlist
let track_start_index; // for reordering of tracks: track start index
let track_stop_index; // for reordering of tracks: track finish index

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

// Page request
const pageRequest = async (offset) => {
	const res = await axios.get(
		`${BASE_URL}/spotify/playlists?limit=${LIMIT}&offset=${offset}`
	);

	const playlists = res.data.spot_playlists;
	const total_spot_playlists = res.data.total_spot_playlists;
	const html = await makeSpotPlaylists(playlists, total_spot_playlists);
	$('#spotPlaylists').html(html);
};

// Display the next page of Spotify playlists
const nextPage = async () => {
	console.debug('nextPage');

	offset += 10;

	pageRequest(offset);
};

// Display the previous page of Spotify playlists
const prevPage = async () => {
	console.debug('prevPage');

	offset -= 10;
	if (offset < 0) offset = 0;

	pageRequest(offset);
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
	// Toggle button color and change text from Send to Sync
	$playlist
		.children('.spotSync')
		.text('Sync')
		.removeClass('btn-success')
		.addClass('btn-light');
	// Refresh the list of Spotify Playlists
	pageRequest(offset);
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
	currentPlaylist = id;

	tracks = await axios.get(`${BASE_URL}/playlists/${id}/tracks`);

	playlist_tracks = '';
	for (let track of tracks.data.tracks) {
		playlist_tracks += `<li class="ui-state-default"><span class="ui-icon ui-icon-arrowthick-2-n-s"></span>
        <iframe src="https://open.spotify.com/embed/track/${track}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
        </li>`;
	}
	$('#playlistTracks').html(playlist_tracks);
};

const moveTrack = async (track_start_index, track_stop_index) => {
	console.debug('moveTrack');
	payload = {
		current_index: track_start_index,
		new_index: track_stop_index
	};
	const res = await axios.patch(
		`${BASE_URL}/playlists/${currentPlaylist}/track`,
		payload
	);
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

$('.sortable').sortable({
	start: function(e, ui) {
		// Returns index of item being moved
		track_start_index = ui.item.index();
	},
	stop: function(e, ui) {
		// Returns index where item is dropped
		track_stop_index = ui.item.index();

		// Playlist already created and in database, update db

		moveTrack(track_start_index, track_stop_index);
	},
	placeholder: 'ui-state-highlight'
});

$body.on('click', '#next', nextPage);
$body.on('click', '#previous', prevPage);
$body.on('click', '.spotSync', spotSync);
$body.on('click', '.showSpotPlaylist', showSpotPlaylist);
$body.on('click', '.showList', showPlaylist);
