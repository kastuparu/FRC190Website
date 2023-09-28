from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, DateField, TimeField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

from website import settings


class CreateEventForm(FlaskForm):
    category_choices = [('', '')] + [(x, x) for x in settings['event_categories']]

    title = StringField("Event Title", validators=[DataRequired(), Length(max=50)])
    category = SelectField("Category", choices=category_choices, validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired(), Length(max=50)])

    start_date = DateField("Start Date:", validators=[DataRequired()])
    start_time = TimeField("Start Time:", validators=[DataRequired()])
    end_date = DateField("End Date:  ", validators=[DataRequired()])
    end_time = TimeField("End Time:  ", validators=[DataRequired()])

    repeats_until = DateField("Repeats Weekly Until (optional):", validators=[Optional()])

    details = TextAreaField("Event Details", validators=[Length(max=500)])
    sign_up_link = StringField("Sign Up Link (optional)", validators=[Length(max=200)])
    submit = SubmitField("Create Event")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.start_date.data:
            self.start_date.data = datetime.now().date()
            self.start_time.data = datetime.now().time()
            self.end_date.data = datetime.now().date()
            self.end_time.data = datetime.now().time()

    def validate(self, **kwargs):
        rv = FlaskForm.validate(self)
        if rv:
            if self.start_date.data > self.end_date.data:
                self.end_date.errors.append("End date must be set after the start date.")
                return False
            elif self.start_date.data == self.end_date.data and self.start_time.data > self.end_time.data:
                self.end_time.errors.append("End time must be set after the start time.")
                return False
            elif self.repeats_until.data and self.repeats_until.data < self.start_date.data:
                self.repeats_until.errors.append("Repeats until date must be set after the start date.")
                return False
            return True
        return False
