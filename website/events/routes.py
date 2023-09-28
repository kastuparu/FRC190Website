from datetime import datetime, timedelta

from flask import render_template, url_for, redirect, flash, request, Blueprint
from flask_login import current_user, login_required

from website import db
from website.models import Event
from website.events.forms import CreateEventForm
from website.main.routes import format_date
from website.events.utils import today_midnight, week_n


events = Blueprint('events', __name__)


@events.route('/events', defaults={'weeks_diff': 0}, methods=['GET', 'POST'])
@events.route('/events/<int(signed=True):weeks_diff>', methods=['GET', 'POST'])
@login_required
def weekly_events(weeks_diff=0):
    today = today_midnight()
    week_start = today - timedelta(days=today.weekday()) + timedelta(days=7 * weeks_diff)
    week_end = week_start + timedelta(days=7)
    week_of = f"Week of {format_date(week_start.timestamp())}"

    event_list = Event.query.filter(Event.start_date.between(week_start.timestamp(), week_end.timestamp())).all()
    if event_list:
        event_list.sort(key=lambda x: x.start_date)
    return render_template('weekly_events.html', title="Events - " + week_of, events=event_list, weeks_diff=weeks_diff)


@events.route('/plan_attendance/<int:event_id>/<action>')
@login_required
def plan_attendance(event_id, action):
    event = Event.query.get_or_404(event_id)
    if action == 'sign_up':
        current_user.sign_up(event)
        flash(f"You are signed up for {event.title} on {format_date(event.start_date)}.", 'success')
    elif action == 'quit':
        current_user.quit(event)
        flash(f"You are no longer signed up for {event.title} on {format_date(event.start_date)}.", 'success')
    db.session.commit()
    return redirect(url_for('events.weekly_events', weeks_diff=week_n(datetime.fromtimestamp(event.start_date))))


@events.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if not current_user.admin:
        return redirect(request.referrer)

    form = CreateEventForm()
    if form.validate_on_submit():

        start_datetime = datetime.combine(form.start_date.data, form.start_time.data)
        end_datetime = datetime.combine(form.end_date.data, form.end_time.data)

        start_datetimes = [start_datetime]
        end_datetimes = [end_datetime]

        if form.repeats_until.data:
            repeats_until = datetime.combine(form.repeats_until.data, form.start_time.data)
            days_between = (repeats_until - start_datetime).days
            start_datetimes = [start_datetime + timedelta(days=x) for x in range(days_between)][::7]
            end_datetimes = [end_datetime + timedelta(days=x) for x in range(days_between)][::7]

        for i in range(len(start_datetimes)):
            event = Event(start_date=start_datetimes[i].timestamp(), end_date=end_datetimes[i].timestamp(),
                          title=form.title.data, category=form.category.data, location=form.location.data,
                          details=form.details.data, sign_up_link=form.sign_up_link.data)
            db.session.add(event)
            db.session.commit()

        if len(start_datetimes) > 1:
            flash(f"{len(start_datetimes)} {form.title.data} events have been created.", 'success')
        else:
            flash(f"The event {form.title.data} on {format_date(start_datetime.timestamp())} has been created.",
                  'success')
        return redirect(url_for('events.weekly_events', weeks_diff=week_n(start_datetimes[0])))
    return render_template('create_event.html', title="Create Event", form=form)


@events.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if not current_user.admin:
        return redirect(request.referrer)

    event = Event.query.get_or_404(event_id)
    form = CreateEventForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.category = form.category.data
        event.location = form.location.data
        event.start_date = datetime.combine(form.start_date.data, form.start_time.data).timestamp()
        event.end_date = datetime.combine(form.end_date.data, form.end_time.data).timestamp()
        event.sign_up_link = form.sign_up_link.data
        event.details = form.details.data
        db.session.commit()
        flash(f"The event {event.title} on {format_date(event.start_date)} has been updated.", 'success')
        return redirect(url_for('events.weekly_events', weeks_diff=week_n(datetime.fromtimestamp(event.start_date))))
    elif request.method == 'GET':
        form.title.data = event.title
        form.category.data = event.category
        form.location.data = event.location
        form.start_date.data = datetime.fromtimestamp(event.start_date).date()
        form.start_time.data = datetime.fromtimestamp(event.start_date).time()
        form.end_date.data = datetime.fromtimestamp(event.end_date).date()
        form.end_time.data = datetime.fromtimestamp(event.end_date).time()
        form.sign_up_link.data = event.sign_up_link
        form.details.data = event.details
        form.submit.label.text = "Update Event"
    return render_template('create_event.html', title='Edit Event', form=form)


@events.route('/delete_event/<int:event_id>')
@login_required
def delete_event(event_id):
    if not current_user.admin:
        return redirect(request.referrer)

    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash(f"The event {event.title} on {format_date(event.start_date)} has been deleted.", 'success')
    return redirect(url_for('events.weekly_events', weeks_diff=week_n(datetime.fromtimestamp(event.start_date))))
