from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from database import db, seed_movies, recalculate_rankings, Movies
import os
from dotenv import load_dotenv

from rate_movie import RateMovieForm, AddMovieForm
from movie_db_api import GetMovie

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
    if request.method == "GET":
        movie_id = request.args.get("id", type=int)
        url = f'https://api.themoviedb.org/3/movie/{movie_id}'
        movie = GetMovie(url=url, token=API_token,query=None)

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

    movie_query = GetMovie(query=query, token=API_token, url=url)
    data = movie_query.get_movie()
    results = data.get("results", [])

    if selected_id:
        selected_movie = next((movie for movie in results if movie.get("id") == selected_id), None)
        if selected_movie is None:
            return redirect(url_for("select_movie", query=query))

        title = selected_movie.get("title") or selected_movie.get("original_title") or "Untitled"
        existing_movie = db.session.execute(
            db.select(Movies).where(Movies.title == title)
        ).scalar_one_or_none()
        if existing_movie:
            return redirect(url_for("home"))

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
        return redirect(url_for("edit", id=new_movie.id))

    return render_template("select.html", movies=results, query=query)

if __name__ == '__main__':
    app.run(debug=True)
