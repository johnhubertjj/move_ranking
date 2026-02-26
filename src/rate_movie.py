"""
WTForms definitions for movie rating and add-movie flows.

This module contains Flask-WTF form classes used by the edit and add pages.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp


def rating_structure():
    return Regexp(
        r"^(10(?:\.0)?|[0-9](?:\.[0-9])?)$",
        message="Rating must be a whole number or one decimal place between 0 and 10.",
    )


class RateMovieForm(FlaskForm):
    """Form used to capture a user rating and review for a movie."""

    rating = StringField("Your Rating out of 10 eg 7.5", validators=[DataRequired(), rating_structure()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    """Form used to capture a movie title search query."""

    title = StringField("Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")
