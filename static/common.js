const $body = $('body');

BASE_URL = '/api';

let playlistTracks = []; // ordered list of dicts: { track name,  track id }
let currentPlaylist; // id of current playlist
let track_start_index; // for reordering of tracks: track start index
let track_stop_index; // for reordering of tracks: track finish index

// Create the HTML to display the playlist tracks
const makePlaylistHTML = (name, id) => {
	return `<li data-id=${id} data-name=${name} class="ui-state-default"> <span class="ui-icon ui-icon-arrowthick-2-n-s"></span> ${name} <button class="del-track btn btn-danger btn-sm "><i class="fa fa-trash" aria-hidden="true"></i></button></li>`;
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

// Delete track in db and update display
const deleteTrack = async (e) => {
	console.debug('deleteTrack');

	const $track = $(e.target).closest('li');
	const id = $track.data('id');

	payload = { id: [ id ] };

	if (currentPlaylist) {
		console.debug('Send patch to delete track');
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
	e.preventDefault();
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
        height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>  <button
        class="btn btn-info btn-sm addToPlaylist mx-2 mb-4">Add</button>
        </p>`;
	}
	return html;
};

const moveTrack = async (track_start_index, track_stop_index) => {
	payload = {
		current_index: track_start_index,
		new_index: track_stop_index
	};
	const res = await axios.patch(
		`${BASE_URL}/playlists/${currentPlaylist}/track`,
		payload
	);
};

//=====================DOM Listeners=============================

// Handle drag and drop of playlist tracks
$('.sortable').sortable({
	start: function(e, ui) {
		// Returns index of item being moved
		track_start_index = ui.item.index();
	},
	stop: function(e, ui) {
		// Returns index where item is dropped
		track_stop_index = ui.item.index();

		// Playlist already created and in database, update db
		if (currentPlaylist) {
			moveTrack(track_start_index, track_stop_index);
		} else {
			// Playlist not sent to db yet
			// Clear list and create track list in new order
			playlistTracks = [];
			$('#playList > li').each(function(index) {
				playlistTracks.push({
					name: $(this).data('name'),
					id: $(this).data('id')
				});
			});
		}
	},
	placeholder: 'ui-state-highlight'
});

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
$('iframe').hover(showAudioFeatures);
