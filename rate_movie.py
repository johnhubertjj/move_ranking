from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp

def rating_structure():
    return Regexp(
        r"^(10(?:\.0)?|[0-9](?:\.[0-9])?)$",
        message="Rating must be a whole number or one decimal place between 0 and 10.",
    )

class RateMovieForm(FlaskForm):
        rating = StringField('Your Rating out of 10 eg 7.5', validators=[DataRequired(), rating_structure()])
        review = StringField('Your Review', validators=[DataRequired()])
        submit = SubmitField('Done')

class AddMovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')
