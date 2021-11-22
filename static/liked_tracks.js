// AJAX file for /tracks (Spotify liked tracks)

const LIMIT = 25;
let offset = 0; // current search page offset

// Page request
const pageRequest = async (offset) => {
	const res = await axios.get(`${BASE_URL}/me/tracks?offset=${offset}`);
	const tracks = res.data.track_dicts;
	const html = await makeTracksHTML(tracks);
	$('#tracks').html(html);
};

// Display the next page of Spotify liked tracks
const nextPage = async () => {
	console.debug('nextPage');

	offset += 20;

	pageRequest(offset);
};

// Display the previous page of Spotify liked tracks
const prevPage = async () => {
	console.debug('prevPage');

	offset -= 20;
	if (offset < 0) offset = 0;

	pageRequest(offset);
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

//=====================DOM Listeners=============================

$body.on('click', '#next', nextPage);
$body.on('click', '#previous', prevPage);
