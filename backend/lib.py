from __future__ import annotations

import os
import time
from base64 import b64encode
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from httpx import AsyncClient

class SpotifyAuth:
	def __init__(self, client_id: str, client_secret: str, refresh_token: str):
		self.client_id = client_id
		self.client_secret = client_secret
		self.refresh_token = refresh_token
		self.access_token: str | None = None
		self.expires_at: float = 0

		if os.getenv('DEV_MODE') == 'True':
			self.access_token = os.getenv('DEV_SPOTIFY_ACCESS_TOKEN')
			self.expires_at = float('inf')

	async def get_access_token(self, client: AsyncClient) -> str:
		if self.access_token and time.time() < self.expires_at - 30:
			return self.access_token
		
		
		basic_auth = b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

		res = await client.post(
			'https://accounts.spotify.com/api/token',
			headers = {
				'Authorization': f'Basic {basic_auth}',
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			data = {
				'grant_type': 'refresh_token',
				'refresh_token': self.refresh_token
			}
		)

		res.raise_for_status()
		data = res.json()

		self.access_token = data['access_token']
		self.expires_at = time.time() + data['expires_in']
		return self.access_token # type: ignore