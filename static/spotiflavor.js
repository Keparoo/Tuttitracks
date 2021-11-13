const $body = $('body');

const handleAdd = async (e) => {
	e.preventDefault();
	console.debug('handleAdd');
};

$body.on('click', '.addToPlaylist', handleAdd);
