import os
import time

from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Annotated, Optional
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from httpx import AsyncClient
from psycopg_pool import ConnectionPool
from datetime import datetime, timezone

from lib import SpotifyAuth

load_dotenv()
spotify = SpotifyAuth(
	client_id=os.getenv('SPOTIFY_CLIENT_ID'), # pyright: ignore[reportArgumentType]
	client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'), # pyright: ignore[reportArgumentType]
	refresh_token=os.getenv('SPOTIFY_REFRESH_TOKEN') # pyright: ignore[reportArgumentType]
)

pool = ConnectionPool(
	os.getenv('DB_URL'),
	min_size=1,
	max_size=5
)

@asynccontextmanager
async def lifespan(app: FastAPI):
	async with AsyncClient() as client:
		yield {'client': client}

app = FastAPI(lifespan=lifespan)

origins = [
	'http://localhost:8080',
	'https://wao.my.id'
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=['*'],
	allow_headers=['*'],
)

templates = Jinja2Templates(directory="backend/templates")

def get_client(request: Request) -> AsyncClient:
	return request.state.client

@app.get('/')
async def read_root():
	return {'Hello': 'World'}

_now_playing_cache: dict | None = None
_now_playing_cache_timestamp = 0
now_playing_cache_ttl = 5 if os.environ.get('DEV_MODE') == 'True' else 30 # seconds

@app.get('/nowplaying')
async def now_playing(request: Request, client: AsyncClient = Depends(get_client)):
	global _now_playing_cache, _now_playing_cache_timestamp
	
	now = time.time()
	if _now_playing_cache and (now - _now_playing_cache_timestamp) < now_playing_cache_ttl:
		return _now_playing_cache

	access_token = await spotify.get_access_token(client)

	res = await client.get(
		'https://api.spotify.com/v1/me/player/currently-playing',
		headers = {'Authorization': f'Bearer {access_token}'}
	)

	if res.status_code == 204:
		return {'playing': False}
	
	if res.status_code != 200:
		raise HTTPException(
			status_code=res.status_code,
			detail=f'Failed to fetch currently playing track from Spotify: {res.text}'
		)
	
	data: dict = res.json()
	item: dict = data.get('item') # type: ignore
	album: dict = item.get('album', {})
	images: list[dict] = album.get('images', [])

	if not item:
		return {'playing': False}
	
	result = {
		'playing': data['is_playing'],
		'artists': [
			{
				'name': artist['name'],
				'url': artist['external_urls']['spotify']
			} for artist in item.get('artists', [])
		],
		'album': {
			'name': album.get('name'),
			'url': album.get('external_urls', {}).get('spotify'),
			'images': images[1]['url'] if len(images) == 3 else images[0]['url']
		},
		'track': {
			'name': item.get('name'),
			'url': item.get('external_urls', {}).get('spotify')
		}
	}

	_now_playing_cache = result
	_now_playing_cache_timestamp = now
	return result

@app.get('/nowplaying/example')
def now_playing_example():
	return {
		'playing': True,
		'artists': [
			{
				'name': 'underscores',
				'url': 'https://open.spotify.com/artist/7HfUJxeVTgrvhk0eWHFzV7'
			},
			{
				'name': 'gabby start',
				'url': 'https://open.spotify.com/artist/33L1klom7IXmoAP8fjrGm9'
			}
		],
		'album': {
			'name': 'Wallsocket',
			'url': 'https://open.spotify.com/album/0mQPq9INcTC48siErksOrl',
			'images': 'https://i.scdn.co/image/ab67616d00001e02f03fa3edc4db4b145655550d'
		},
		'track': {
			'name': 'Locals (Girls like us) [with gabby start]',
			'url': 'https://open.spotify.com/track/42FM6tM3n06euZCvpJn3dn'
		}
	}

@app.get('/guestbook')
def guestbook(request: Request, start: int = 0):
	print(start)
	with pool.connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				'SELECT id, name, message, created FROM guestbook ORDER BY id DESC LIMIT 100'
			)
			entries = cur.fetchall()

	print(entries)

	formatted_entries = []
	for entry in entries:
		id: int
		name: Optional[str]
		message: str
		created: datetime
		id, name, message, created = entry
		formatted_entries.append({
			'id': id,
			'name': name if name is not None else 'Anonymous',
			'message': message,
			'created': created.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
			'createdRaw': created.astimezone(timezone.utc).isoformat()
		})

	print(formatted_entries)

	return templates.TemplateResponse(
		request=request,
		name="guestbook.html",
		context={
			'entries': formatted_entries,
			'start': start
		}
	)

@app.post('/guestbook')
def guestbook_post(
	message: Annotated[str, Form()],
	anonymous: Annotated[bool, Form()] = False,
	name: Annotated[Optional[str], Form()] = None
):
	print(f'Guestbook entry: anonymous={anonymous}, name={name}, message={message}')

	if anonymous:
		name = None

	if name is not None and len(name.strip()) == 0:
		name = None

	if name is not None and len(name.strip()) > 128:
		raise HTTPException(status_code=400, detail='Name is too long (max 128 characters)')
	
	if len(message.strip()) == 0:
		raise HTTPException(status_code=400, detail='Message cannot be empty')
	
	if len(message.strip()) > 512:
		raise HTTPException(status_code=400, detail='Message is too long (max 512 characters)')
	
	name = name.strip() if name is not None else None
	message = message.strip()

	with pool.connection() as conn:
		with conn.cursor() as cur:
			cur.execute(
				'INSERT INTO guestbook (name, message) VALUES (%s, %s)',
				(name, message)
			)
		conn.commit()

	return RedirectResponse(url='/guestbook', status_code=303)