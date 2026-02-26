"""
Database models and persistence helpers for the movie app.

This module defines the SQLAlchemy instance, ORM models, and helper
functions used to seed data and maintain ranking order.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy ORM models."""

    pass


db = SQLAlchemy(model_class=Base)


class Movies(db.Model):
    """ORM model representing a movie entry displayed in the app."""

    __tablename__ = "Movie"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Float, nullable=False)
    review = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String, nullable=False)


def seed_movies() -> None:
    db.create_all()

    samples = [
        {
            "title": "Phone Booth",
            "year": 2002,
            "description": "A publicist is trapped in a phone booth by a mysterious caller.",
            "rating": 7.3,
            "ranking": 10,
            "review": "My favourite character was the caller.",
            "img_url": "https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg",
        },
        {
            "title": "Avatar The Way of Water",
            "year": 2022,
            "description": "The Sully family faces new threats and fights to stay together.",
            "rating": 7.3,
            "ranking": 9,
            "review": "I liked the water.",
            "img_url": "https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
        },
    ]

    for sample in samples:
        exists = db.session.query(Movies).filter_by(title=sample["title"]).first()
        if not exists:
            db.session.add(Movies(**sample))

    db.session.commit()


def recalculate_rankings() -> None:
    movies = db.session.execute(
        db.select(Movies).order_by(Movies.rating.desc(), Movies.id.asc())
    ).scalars().all()

    for rank, movie in enumerate(movies, start=1):
        movie.ranking = rank
