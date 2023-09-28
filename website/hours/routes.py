from datetime import datetime

from flask import render_template, url_for, redirect, flash, request, Blueprint
from flask_login import current_user, login_required

from website import db, settings
from website.hours.forms import LogHoursForm
from website.models import User, Event, Hours
from website.events.utils import week_n


hours = Blueprint('hours', __name__)


@hours.route('/log_hours/<int:event_id>', methods=['GET', 'POST'])
@login_required
def log_hours(event_id):
    event = Event.query.get_or_404(event_id)
    previously_existing = Hours.query.filter_by(user_id=current_user.id, event_id=event.id).first()
    form = LogHoursForm(event.start_date, event.end_date)
    form.event = event

    if form.validate_on_submit():
        start_datetime = datetime.combine(form.end_date.data, form.end_time.data)
        end_datetime = datetime.combine(form.start_date.data, form.start_time.data)
        duration_hrs = (start_datetime - end_datetime).total_seconds() / 3600
        logged_hours = Hours(duration=duration_hrs, approved=False, user_id=current_user.id, event_id=event.id)

        if previously_existing:
            db.session.delete(previously_existing)
        db.session.add(logged_hours)
        db.session.commit()
        flash(f"{duration_hrs} hours logged for {event.title}, {event.category}.", 'success')
        return redirect(url_for('events.weekly_events', weeks_diff=week_n(datetime.fromtimestamp(event.start_date))))

    elif request.method == 'GET':
        form.start_date.data = datetime.fromtimestamp(event.start_date).date()
        form.end_date.data = datetime.fromtimestamp(event.end_date).date()
        form.start_time.data = datetime.fromtimestamp(event.start_date).time()
        form.end_time.data = datetime.fromtimestamp(event.end_date).time()
    return render_template('log_hours.html', title="Log Hours", event=event, form=form,
                           previously_existing=bool(previously_existing))


@hours.route('/manage_hours')
@login_required
def manage_hours():
    if not current_user.admin:
        return redirect(request.referrer)
    hours_types = settings['event_categories']
    students = User.query.filter(User.position.in_(settings['student_types'])).all()
    mentors = User.query.filter(User.position.in_(settings['mentor_types'])).all()
    if students:
        students.sort(key=lambda x: (x.last_name, x.first_name))
    if mentors:
        mentors.sort(key=lambda x: (x.last_name, x.first_name))
    hours_list = Hours.query.filter_by(approved=False).all()
    return render_template('manage_hours.html', title="Manage Hours", students=students, mentors=mentors,
                           hours_list=hours_list, hours_types=hours_types)


@hours.route('/approve_hours/<int:hours_id>')
@login_required
def approve_hours(hours_id):
    if not current_user.admin:
        return redirect(request.referrer)
    hours_for_approval = Hours.query.get_or_404(hours_id)
    hours_for_approval.approved = True
    db.session.commit()
    flash(f"{hours_for_approval.duration} hours approved for {hours_for_approval.user.first_name} "
          f"{hours_for_approval.user.last_name}.", 'success')
    return redirect(url_for('hours.manage_hours'))


@hours.route('/delete_hours/<int:hours_id>')
@login_required
def delete_hours(hours_id):
    if not current_user.admin:
        return redirect(request.referrer)
    hours_to_delete = Hours.query.get_or_404(hours_id)
    db.session.delete(hours_to_delete)
    db.session.commit()
    flash(f"Hours not approved for {hours_to_delete.user.first_name} {hours_to_delete.user.last_name}.", 'success')
    return redirect(url_for('hours.manage_hours'))
