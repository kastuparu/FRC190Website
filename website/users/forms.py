from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, BooleanField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from website import settings
from website.models import User


class RegistrationForm(FlaskForm):
    position_choices = [('', '')] + [(x, x) for x in settings['student_types'] + settings['mentor_types']]

    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=2, max=20)])
    position = SelectField("Position", validators=[DataRequired()], choices=position_choices)
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=5)])
    password_confirmation = PasswordField("Confirm Password", validators=[EqualTo('password')])
    submit = SubmitField("Register User")

    def validate_email(form, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("A user with this email already exists.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")


class UpdateBioForm(FlaskForm):
    bio = StringField("Bio", description="Write your bio here", validators=[Length(max=150)])
    submit = SubmitField("Update Bio")


class UpdateProfilePictureForm(FlaskForm):
    picture = FileField("Profile Picture", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField("Update Profile Pic")


class AddBulkUsersForm(FlaskForm):
    bulk_users = TextAreaField("Paste CSV Data", validators=[DataRequired()])
    submit = SubmitField("Add Users")
