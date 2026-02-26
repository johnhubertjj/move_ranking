"""
Flask application entry point for the Top Movies project.

This module configures the Flask app, routes, database integration, and
TMDB-backed add/select workflow for managing the movie list.
"""

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from src.database import db, seed_movies, recalculate_rankings, Movies
import os
from dotenv import load_dotenv

from src.rate_movie import RateMovieForm, AddMovieForm
from src.select_movie_service import process_movie_selection

# Get movie stuff
load_dotenv()
API_token=os.getenv("MOVIE_DB_TOKEN")

url = "https://api.themoviedb.org/3/search/movie?include_adult=false&language=en-US&page=1"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db.init_app(app)

with app.app_context():
    seed_movies()


@app.route("/")
def home():
    all_movies = db.session.execute(db.select(Movies).order_by(Movies.ranking)).scalars().all()
    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=["GET", "POST"])
def edit():
    movie_id = request.args.get("id", type=int)
    movie = db.get_or_404(Movies, movie_id)
    form = RateMovieForm()

    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        recalculate_rankings()
        db.session.commit()
        return redirect(url_for("home"))

    if request.method == "GET":
        form.rating.data = str(movie.rating)
        form.review.data = movie.review

    return render_template("edit.html", form=form, movie=movie)

@app.route("/delete", methods=["POST"])
def delete_movie():
    movie_id = request.args.get("id", type=int)
    movie = db.get_or_404(Movies, movie_id)
    db.session.delete(movie)
    recalculate_rankings()
    db.session.commit()
    return redirect(url_for("home"))

@app.route('/add', methods=["GET", "POST"])
def add_movie():
    form = AddMovieForm()

    if form.validate_on_submit():
        movie_title = form.title.data.strip()
        return redirect(url_for("select_movie", query=movie_title))

    return render_template("add.html", form=form)

@app.route('/select', methods=["GET", "POST"])
def select_movie():
    query = (request.args.get("query") or "").strip()
    selected_id = request.args.get("id", type=int)

    if not query:
        return redirect(url_for("add_movie"))

    result = process_movie_selection(
        query=query,
        selected_id=selected_id,
        api_token=API_token,
        search_url=url,
    )

    if result["status"] == "not_found":
        return redirect(url_for("select_movie", query=query))

    if result["status"] == "duplicate":
        return redirect(url_for("home"))

    if result["status"] == "added":
        return redirect(url_for("edit", id=result["movie"].id))

    return render_template("select.html", movies=result["results"], query=query)

if __name__ == '__main__':
    app.run(debug=True)
