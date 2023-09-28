from datetime import datetime, timedelta

from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, TimeField
from wtforms.validators import DataRequired

from website.models import Event


class LogHoursForm(FlaskForm):

    start_date = DateField("Start Date", validators=[DataRequired()])
    start_time = TimeField("Start Time", validators=[DataRequired()])
    end_date = DateField("End Date", validators=[DataRequired()])
    end_time = TimeField("End Time", validators=[DataRequired()])
    submit = SubmitField("Log Hours")

    def __init__(self, event_start: int, event_end: int, buffer_hours=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        buffer = timedelta(hours=buffer_hours)
        self.event_start = datetime.fromtimestamp(event_start) - buffer
        self.event_end = datetime.fromtimestamp(event_end) + buffer

    def validate(self, **kwargs):
        if FlaskForm.validate(self):
            if self.start_date.data > self.end_date.data:
                self.end_date.errors.append("End date must be set after the start date.")
                return False
            elif self.start_date.data == self.end_date.data and self.start_time.data > self.end_time.data:
                self.end_time.errors.append("End time must be set after the start time.")
                return False
            elif datetime.combine(self.start_date.data, self.start_time.data) > datetime.now():
                self.start_date.errors.append("Hours occurring in the future cannot be logged.")
                return False
            elif datetime.combine(self.start_date.data, self.start_time.data) < self.event_start:
                self.start_date.errors.append("Hours occurring too far before the event cannot be logged.")
                return False
            elif datetime.combine(self.end_date.data, self.end_time.data) > self.event_end:
                self.end_date.errors.append("Hours occurring too far after the event cannot be logged.")
                return False
            return True
        return False
