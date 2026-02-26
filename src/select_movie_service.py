"""
Selection workflow helpers for TMDB search results.

This module encapsulates the non-route logic used by the ``/select`` Flask
endpoint to fetch TMDB search results and add a selected movie to the local
application database.
"""

from src.database import db, Movies
from src.movie_db_api import GetMovie


def process_movie_selection(query, selected_id, api_token, search_url):
    """Fetch search results and optionally add a selected movie to the database.

    :param query: User-entered movie title search text.
    :type query: str
    :param selected_id: TMDB movie identifier selected by the user.
    :type selected_id: int | None
    :param api_token: TMDB API bearer token.
    :type api_token: str
    :param search_url: TMDB search endpoint URL.
    :type search_url: str
    :returns: A result dictionary with keys ``status``, ``results``, and
        optionally ``movie`` when a movie is added.
    :rtype: dict
    """
    movie_query = GetMovie(query=query, token=api_token, url=search_url)
    data = movie_query.get_movie()
    results = data.get("results", [])

    if not selected_id:
        return {"status": "render", "results": results}

    selected_movie = next((movie for movie in results if movie.get("id") == selected_id), None)
    if selected_movie is None:
        return {"status": "not_found", "results": results}

    title = selected_movie.get("title") or selected_movie.get("original_title") or "Untitled"
    existing_movie = db.session.execute(
        db.select(Movies).where(Movies.title == title)
    ).scalar_one_or_none()
    if existing_movie:
        return {"status": "duplicate", "results": results, "movie": existing_movie}

    existing_movies = db.session.execute(db.select(Movies)).scalars().all()
    for movie in existing_movies:
        movie.ranking += 1

    release_date = selected_movie.get("release_date") or ""
    year = int(release_date[:4]) if release_date[:4].isdigit() else 0
    poster_path = selected_movie.get("poster_path")
    img_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
    rating = round(float(selected_movie.get("vote_average") or 0), 1)

    new_movie = Movies(
        title=title,
        year=year,
        description=selected_movie.get("overview") or "No overview available.",
        rating=rating,
        ranking=1,
        review="",
        img_url=img_url,
    )
    db.session.add(new_movie)
    db.session.commit()

    return {"status": "added", "results": results, "movie": new_movie}
