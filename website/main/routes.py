from datetime import datetime, date

from flask import render_template, Blueprint

from website import app

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html', title="FRC Team 190")


@main.route('/about')
def about():
    return render_template('about.html', title="About Team 190")


@main.route('/demos')
def demos():
    return render_template('demos.html', title="Demos")


@main.route('/outreach_events')
def outreach_events():
    return render_template('outreach_events.html', title="Outreach Events")


@app.template_filter()
def format_datetimes(start, end):
    start_datetime = datetime.fromtimestamp(start)
    end_datetime = datetime.fromtimestamp(end)
    current_year = datetime.now().year == end_datetime.year

    date_str = ''

    start_datetime_format = '%A %B %-d, ' + ('%Y, ' if not current_year else '') + '%-I:%M %p'
    date_str += start_datetime.strftime(start_datetime_format) + ' - '

    end_datetime_format = '%-I:%M %p'
    if start_datetime.date() != end_datetime.date():
        end_datetime_format = '%A %B %-d, ' + ('%Y, ' if not current_year else '') + '%-I:%M %p'
    date_str += end_datetime.strftime(end_datetime_format)

    return date_str


@app.template_filter()
def format_date(date_timestamp):
    date_time = datetime.fromtimestamp(date_timestamp)
    new_format = '%A %B %-d'

    if datetime.now().year != date.year:
        new_format += ', %Y'

    return date_time.strftime(new_format)
