// AJAX file for /top route (top tracks)

LIMIT = 25; // Number of tracks per page
// time_range is the time frame top tracks are calculated:
// long_term=several years including new data as available, medium_term=approx 6 months (Spotify default), short_term=approx 4 weeks
TIME_RANGE = 'medium_term';
let offset = 0; // current search page offset

// Page request
const pageRequest = async (offset) => {
	const res = await axios.get(
		`${BASE_URL}/me/top/tracks?limit=${LIMIT}&offset=${offset}&time_range=${TIME_RANGE}`
	);
	const tracks = res.data.tracks;
	const html = await makeTracksHTML(tracks);
	$('#tracks').html(html);
};

// Display the next page of top tracks
const nextPage = async () => {
	console.debug('nextPage');

	offset += 20;

	pageRequest(offset);
};

// Display the previous page of top tracks
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
