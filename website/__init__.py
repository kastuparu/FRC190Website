from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app_version = '1.0.0'
app = Flask(__name__)
app.config['SECRET_KEY'] = '1779a432af577b347e5bafd92119971506f90ae7746b93db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
settings = {
    "student_types": ["Mass Academy '24", "Mass Academy '25", "High School Student"],
    "mentor_types": ["WPI Student Mentor", "Mentor"],
    "event_categories": ["Work Hours", "Team Meeting", "Demo", "Volunteering", "Off-Season", "Competition"]
}


from website.main.routes import main
from website.events.routes import events
from website.hours.routes import hours
from website.users.routes import users

app.register_blueprint(main)
app.register_blueprint(events)
app.register_blueprint(hours)
app.register_blueprint(users)
