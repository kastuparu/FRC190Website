from datetime import datetime, timedelta

from website import db, login_manager, settings
from flask_login import UserMixin


'''
User <- Hours   one-to-many
User <-> Event  many-to-many
Event <- Hours  one-to-many
'''


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    bio = db.Column(db.String(150), nullable=True)
    profile_pic_filename = db.Column(db.String(20), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)

    hours = db.relationship('Hours', backref='user')

    def interesting_hours(self):
        one_week_ago = datetime.now() - timedelta(days=7)
        interesting_hours = []
        for hours in self.hours:
            start_date = datetime.fromtimestamp(hours.event.start_date)
            if not hours.approved:
                interesting_hours.append(hours)
            elif start_date > one_week_ago:
                interesting_hours.append(hours)
        interesting_hours.sort(key=lambda x: x.event.start_date, reverse=True)
        return interesting_hours

    def hours_summary(self):
        hours_summary_dict = {category: 0 for category in settings['event_categories']}
        if self.hours:
            one_year_ago = datetime.now() - timedelta(days=365)
            for hours in self.hours:
                start_date = datetime.fromtimestamp(hours.event.start_date)
                if start_date > one_year_ago:
                    hours_summary_dict[hours.event.category] += hours.duration
        return hours_summary_dict

    def sign_up(self, event):
        if not self.is_attending(event):
            event.planned_attendees.append(self)

    def quit(self, event):
        if self.is_attending(event):
            event.planned_attendees.remove(self)

    def is_attending(self, event):
        return self in event.planned_attendees

    def __repr__(self):
        return f"User('{self.email}', '{self.first_name}', '{self.last_name}', '{self.position}')"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Integer, nullable=False)
    end_date = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(25), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    details = db.Column(db.String(500), nullable=True)
    sign_up_link = db.Column(db.String(200), nullable=True)

    planned_attendees = db.relationship('User', secondary='user_event', backref='event')
    hours = db.relationship('Hours', backref='event', cascade='all,delete')

    def __repr__(self):
        return f"Event('{self.start_date}', '{self.title}', '{self.category}', '{self.location}')"


class Hours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Float, nullable=False)
    approved = db.Column(db.Boolean, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    def __repr__(self):
        return f"Hours('{self.type}', '{self.date}', '{self.start_time}', '{self.duration}', '{self.approved}')"


user_event = db.Table('user_event',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column('event_id', db.Integer, db.ForeignKey('event.id')))
