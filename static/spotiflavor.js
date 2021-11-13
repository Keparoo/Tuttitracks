const $body = $('body');

BASE_URL = 'http://127.0.0.1:5000/api';

const playlist = [];

const makePlaylistHTML = (name, id) => {
	return `<li data-id=${id}> ${name} <button class="del-track btn btn-warning btn-sm">X</button></li>`;
};

const updatePlaylist = () => {
	let newTrack = $(makePlaylistHTML(track.name, track.id));
	$('#playList').append(newTrack);
	for (let track of playlist) {
		let newTrack = $(makePlaylistHTML(track.name, track.id));
		$('#playList').append(newTrack);
	}
};

const handleAdd = async (e) => {
	e.preventDefault();
	console.debug('handleAdd');
	const $track = $(e.target).closest('p');
	const id = $track.data('id');
	const name = $track.data('name');
	console.log('Track info:', name, id);

	playlist.push({ name: name, id: id });
	console.log(playlist);
	let newTrack = $(makePlaylistHTML(name, id));
	$('#playList').append(newTrack);
	// send new track to database
	// res = axios.post(`${BASE_URL}/playlist/${id}`);
};

// create playlist: POST /users/<user_id>/playlists
// get playlist: GET /playlists/<playlist_id>
// get playlist items: GET /playlists/<playlist_id>/tracks
// add itmes to playlist: POST /playlists/<playlist_id>/tracks
// update playlist items: PUT /playlists/<playlist_id>/tracks
// remove playlist tracks: DELETE /playlists/<playlist_id>/tracks
// get current user's playlists: GET /me/playlists
// get user's playlists: GET /users/<user_id>/playlists

$body.on('click', '.addToPlaylist', handleAdd);
