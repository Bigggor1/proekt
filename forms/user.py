from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Repeat the password', validators=[DataRequired()])
    name = StringField('Username', validators=[DataRequired()])
    about = TextAreaField("A little bit about yourself")
    submit = SubmitField('Log in')


class LoginForm(FlaskForm):
    email = EmailField('Mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


class SearchForm(FlaskForm):
    search = StringField('Request', validators=[DataRequired()])
    submit = SubmitField('Search')

class GeoForm(FlaskForm):
    geosearch = StringField('Request', validators=[DataRequired()])
    geosubmit = SubmitField('Search')
    geoinfo = {}