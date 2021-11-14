const $body = $('body');

BASE_URL = 'http://127.0.0.1:5000/api';

const playlistTracks = [];
let currentPlaylist;

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
// create playlist: POST /users/<username>/playlists
// update playlist details: PUT /playlists/<playlist_id>
// get playlist: GET /playlists/<playlist_id>
// get playlist items: GET /playlists/<playlist_id>/tracks
// add items to playlist: POST /playlists/<playlist_id>/tracks
// update playlist items: PUT /playlists/<playlist_id>/tracks
// remove playlist tracks: DELETE /playlists/<playlist_id>/tracks
// get current user's playlists: GET /me/playlists
// get user's playlists: GET /users/<username>/playlists

$body.on('click', '.addToPlaylist', handleAdd);
$body.on('click', '#createPlaylist', createPlaylist);
$body.on('click', '.del-track', deleteTrack);

// $('ol.simple_with_drop').sortable({
// 	group: 'no-drop',
// 	handle: 'i.icon-move',
// 	onDragStart: function($item, container, _super) {
// 		// Duplicate items of the no drop area
// 		if (!container.options.drop) $item.clone().insertAfter($item);
// 		_super($item, container);
// 	}
// });
