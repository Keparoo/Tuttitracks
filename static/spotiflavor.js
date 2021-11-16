const $body = $('body');

BASE_URL = 'http://127.0.0.1:5000/api';

const playlistTracks = [];
let currentPlaylist;
let curr_audio_features = [];
let offset = 0;

const makePlaylistHTML = (name, id) => {
	return `<li data-id=${id}> ${name} <button class="del-track btn btn-warning btn-sm">X</button></li>`;
};

const updatePlaylist = () => {
	let newTrack = $(makePlaylistHTML(track.name, track.id));
	$('#playList').append(newTrack);
	for (let track of playlistTracks) {
		let newTrack = $(makePlaylistHTML(track.name, track.id));
		$('#playList').append(newTrack);
	}
};

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
        Loudness: ${features.data.loudness} avg db<br>
        Valence: ${features.data.valence} (0-1)</p>
    </div>
    `;
	// <p> Tempo: ${features.data.tempo} avg bpm</p>
};

const showAudioFeatures = async (e) => {
	console.debug('showAudioFeatures');
	const $p = $(e.target).closest('p');
	const id = $p.data('id');
	let features = await makeFeaturesHTML(id);
	$('#audio-features').html(features);
};

const handleAdd = async (e) => {
	e.preventDefault();
	console.debug('handleAdd');
	const $track = $(e.target).closest('p');
	const id = $track.data('id');
	const spotId = $track.data('spotid');
	const name = $track.data('name');
	console.log('Track info:', name, id, spotId);

	playlistTracks.push({ name: name, id: id });
	console.log(playlistTracks);
	let newTrack = $(makePlaylistHTML(name, id));
	$('#playList').append(newTrack);

	payload = { id: [ id ] };

	if (currentPlaylist) {
		// send new track to database
		const res = await axios.post(
			`${BASE_URL}/playlists/${currentPlaylist}/tracks`,
			payload
		);
		console.log(res.data.playlist_id);
	}
};

const deleteTrack = async (e) => {
	e.preventDefault();
	console.debug('deleteTrack');
	const $track = $(e.target).closest('li');
	const id = $track.data('id');
	console.log('Track to delete: ', id);

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

const createPlaylist = async (e) => {
	e.preventDefault();
	console.debug('createPlaylist');

	const $form = $('#form');
	const $username = $form.data('username');
	console.log($username);
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
		console.debug(res.data.name, res.data.description, res.data.playlist_id);
	} else {
		console.debug('New Playlist');
		const playlist_payload = { name, description, playlistTracks };
		const res = await axios.post(
			`${BASE_URL}/users/${$username}/playlists`,
			playlist_payload
		);
		console.debug(res.data.name, res.data.description, res.data.playlist_id);
		currentPlaylist = res.data.playlist_id;
		$('#createPlaylist').html('Update Playlist');
	}
};

const makeTracksHTML = async (tracks) => {
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

const nextPage = async () => {
	console.debug('nextPage');

	offset += 10;

	const res = await axios.get(`${BASE_URL}/me/tracks?offset=${offset}`);
	const tracks = res.data.track_dicts;
	const html = await makeTracksHTML(tracks);
	$('#tracks').html(html);
};

const prevPage = async () => {
	console.debug('prevPage');

	offset -= 10;
	if (offset < 0) offset = 0;

	const res = await axios.get(`${BASE_URL}/me/tracks?offset=${offset}`);
	const tracks = res.data.track_dicts;
	const html = await makeTracksHTML(tracks);
	$('#tracks').html(html);
};

const spotSync = async (e) => {
	console.debug('spotSync');

	const $playlist = $(e.target).closest('li');
	const id = $playlist.data('id');
	const playlistId = $playlist.data('spotId');

	const res = await axios.post(`${BASE_URL}/spotify/${id}/playlists`);
	if (res.error) {
		console.log(res.message);
	}
	// console.log(res.data.playlist.spotify_track_id);
};

const showSpotPlaylist = async (e) => {
	console.debug('showSpotPlaylist');
	const $playlist = $(e.target).closest('li');
	const id = $playlist.data('spot-id');
	html = `
    <iframe src="https://open.spotify.com/embed/playlist/${id}" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
    `;
	$('#spotPlaylist').html(html);
};

const showPlaylist = async (e) => {
	console.debug('showPlaylist');
	const $playlist = $(e.target).closest('li');
	const id = $playlist.data('id');

	tracks = await axios.get(`${BASE_URL}/playlists/${id}/tracks`);
	console.log(tracks.data.tracks);

	playlist_tracks = '';
	for (let track of tracks.data.tracks) {
		playlist_tracks += `<p>
        <iframe src="https://open.spotify.com/embed/track/${track}" width="300" height="80" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
        </p>`;
	}
	$('#playlistTracks').html(playlist_tracks);
};
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

// $('ol.simple_with_drop').sortable({
// 	group: 'no-drop',
// 	handle: 'i.icon-move',
// 	onDragStart: function($item, container, _super) {
// 		// Duplicate items of the no drop area
// 		if (!container.options.drop) $item.clone().insertAfter($item);
// 		_super($item, container);
// 	}
// });
