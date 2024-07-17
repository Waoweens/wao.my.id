const ws = new WebSocket('ws://localhost:8000/media/nowplaying/Waoweens/ws');

ws.addEventListener('open', () => {
	ws.send('get');
})

const artwork = document.getElementById('songArtwork');
const title = document.getElementById('songTitle');
const artist = document.getElementById('songArtist');
const album = document.getElementById('songAlbum');

ws.addEventListener('message', (event) => {
	const data = JSON.parse(event.data);

	if (data.hasOwnProperty('now_playing')) {
		const song = data.now_playing;

		artwork.src = song.artwork;
		title.textContent = song.title;
		artist.textContent = song.artist;
		album.textContent = song.album;
	}

	if (isEmpty(data)) {
		artwork.src = '/images/nowplaying/empty.png';
		title.textContent = 'Nothing playing';
		artist.textContent = '';
		album.textContent = '';
	}
})

function isEmpty(obj) {
	return Object.keys(obj).length === 0;
}