"""
TMDB API client helpers.

This module contains a small wrapper class used to query The Movie Database
API for movie search results and movie details.
"""

from typing import Any

import requests


class GetMovie:
    """Client wrapper for TMDB movie endpoints.

    :param query: Search text for movie lookup. May be ``None`` for detail calls.
    :param token: TMDB API bearer token.
    :param url: TMDB endpoint URL to request.
    """

    def __init__(self, query: str | None, token: str, url: str) -> None:
        self.query = query
        self.API_token = token
        self.url = url

    def get_movie(self) -> dict[str, Any]:
        if self.query:
            params = {
                'query': self.query,
                'include_adult': True,
                'language': 'en-US',
                'page': 1
            }
        else:
            params = {
                'include_adult': True,
                'language': 'en-US',
                'page': 1
            }


        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.API_token}"
        }
        response = requests.get(self.url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()