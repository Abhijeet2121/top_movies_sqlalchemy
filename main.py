from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_KEY = "1276f554bf434486091718f1d01c4f66"
SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DETAILS_URL = "https://api.themoviedb.org/3/movie"
IMAGE_URL = "https://image.tmdb.org/t/p/original"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
# db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATONS_'] = False
db = SQLAlchemy()
db.init_app(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(250), unique = True, nullable = False)
    year = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String(500), nullable = False)
    rating = db.Column(db.Float, nullable = False)
    ranking = db.Column(db.Integer, nullable = False)
    review = db.Column(db.String(250), nullable = False)
    img_url = db.Column(db.String(250), unique = True, nullable = False)

    def __repr__(self):
        return f"Movie{self.title}"

with app.app_context():
    db.create_all()

class FindMovieForm(FlaskForm):
    title = StringField("Movie title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")

class RateMovieForm(FlaskForm):
    rating = StringField("Your rating out of 10", validators=[DataRequired()])
    review = StringField("Your review", validators=[DataRequired()])
    submit = SubmitField("Done")

@app.route("/")
def home():
    all_movies = db.session.query(Movie).order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        print(all_movies[i].rating)
        print(all_movies[i].ranking == int(len(all_movies) - i))
    db.session.commit()
    return render_template("index.html", movies = all_movies)

@app.route("/add", methods =["GET", "POST"])
def add():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        params = {
            "api_key":API_KEY,
            "query":movie_title
        }
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxMjc2ZjU1NGJmNDM0NDg2MDkxNzE4ZjFkMDFjNGY2NiIsInN1YiI6IjY0NmEwOGRhMDA2YjAxMDE4OTU4ZmE4ZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.zZ6a6sifbiN5zhIv_FU8hiI7-I8juxu4l3EDIdSlyyA"
        }
        response = requests.get(SEARCH_URL, params=params, headers=headers,)
        data = response.json()['results']
        # print(response.text)
        return render_template('select.html', options=data)
    return render_template("add.html", form=form)

@app.route("/find")
def find_movies():
    movie_id = request.args.get('id')
    if movie_id:
        movie_api_url = f"{MOVIE_DETAILS_URL}/{movie_id}"
        params = {
            "api_key": API_KEY,
            "langauge": "en-US"
        }
        response = requests.get(movie_api_url, params=params)
        data = response.json()
        
        new_movie = Movie(
            title = data['title'],
            year = data["release_date"].split("-")[0],
            description = data['overview'],
            rating = 0.1,
            ranking = 1,
            review = "None",
            img_url = f"{IMAGE_URL}{data['poster_path']}",
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect( url_for('rate_movie', id = new_movie.id))

@app.route("/edit", methods = ['GET', 'POST'])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)

    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect( url_for('home'))
    return render_template("edit.html", movie=movie, form=form)

@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect( url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
