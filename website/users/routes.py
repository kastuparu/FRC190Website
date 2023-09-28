import secrets
from email_validator import validate_email, EmailNotValidError

from flask import render_template, url_for, redirect, flash, request, Blueprint
from flask_login import login_user, logout_user, current_user, login_required

from website import bcrypt, db, settings
from website.models import User
from website.users.forms import LoginForm, UpdateBioForm, UpdateProfilePictureForm, AddBulkUsersForm
from website.users.utils import save_profile_picture


users = Blueprint('users', __name__)


'''
@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data)
        user = User(email=form.email.data, password=hashed_pw,                          # type: ignore[call-arg]
                    first_name=form.first_name.data, last_name=form.last_name.data,     # type: ignore[call-arg]
                    position=form.position.data, profile_pic_filename='default.png',    # type: ignore[call-arg]
                    admin=False)                                                        # type: ignore[call-arg]
        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.email.data}", 'success')
        return redirect(url_for('main.home'))
    return render_template('register.html', title="Register", form=form)
'''


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('events.weekly_events'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('events.weekly_events'))
        else:
            flash("Login unsuccessful. Please check email and password.", 'danger')
    return render_template('login.html', title="Log In", form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    bio_form = UpdateBioForm()
    pfp_form = UpdateProfilePictureForm()
    if pfp_form.validate_on_submit() and pfp_form.picture.data:
        picture_filename = save_profile_picture(pfp_form.picture.data)
        current_user.profile_pic_filename = picture_filename
        db.session.commit()
        flash("Your profile picture has been updated.", 'success')
        return redirect(url_for('users.account'))
    if bio_form.validate_on_submit() and bio_form.bio.data != current_user.bio:
        current_user.bio = bio_form.bio.data
        db.session.commit()
        flash("Your bio has been updated.", 'success')
        return redirect(url_for('users.account'))
    bio_form.bio.data = current_user.bio

    hours_types = settings['event_categories']
    hours_summary = current_user.hours_summary()
    interesting_hours = current_user.interesting_hours()

    return render_template('account.html', title="Account", bio_form=bio_form, pfp_form=pfp_form,
                           hours_types=hours_types, hours_summary=hours_summary, interesting_hours=interesting_hours)


@login_required
@users.route('/team')
def team():
    students = User.query.filter(User.position.in_(settings['student_types'])).all()
    if students:
        students.sort(key=lambda x: (x.last_name, x.first_name))
    mentors = User.query.filter(User.position.in_(settings['mentor_types'])).all()
    if mentors:
        mentors.sort(key=lambda x: (x.last_name, x.first_name))
    return render_template('team.html', title="FRC 190 Students and Mentors",
                           students=students, mentors=mentors)


@users.route('/add_bulk_users', methods=['GET', 'POST'])
@login_required
def add_bulk_users():
    if not current_user.admin:
        return redirect(request.referrer)

    form = AddBulkUsersForm()
    if form.validate_on_submit():
        successful_adds = 0
        for line in form.bulk_users.data:
            try:
                first_name, last_name, email, position = line.split(',')
            except ValueError:
                flash(f"'{line}' was not added because it did not follow the format: "
                      f"'first_name,last_name,email,position'.", 'danger')
                continue
            try:
                email = validate_email(email)['email']
            except EmailNotValidError:
                flash(f"{first_name} {last_name} was not added because '{email}' is not a valid email.", 'danger')
                continue
            if position not in settings['student_types'] + settings['mentor_types']:
                flash(f"{first_name} {last_name} was not added because '{position}' is not a valid position.", 'danger')
                continue
            password = secrets.token_hex(4)
            hashed_pw = bcrypt.generate_password_hash(password)

            user = User(email=email, password=hashed_pw, first_name=first_name,             # type: ignore[call-arg]
                        last_name=last_name, position=position,                             # type: ignore[call-arg]
                        profile_pic_filename='default.png', admin=False)                    # type: ignore[call-arg]
            db.session.add(user)
            db.session.commit()
            successful_adds += 1

            # TODO: set up email sending
            # TODO: create password for user, or give them a link to create password?
            f'''
            Hello {first_name} {last_name},
            
                You have been invited to sign up for FRC 190's website. Please log in using the following 
                credentials. Be sure to change your password after logging in.
                
                Website link: frc190.org/login
                Email: {email}
                Password: {password}
                
            Sincerely,
            FRC 190
            '''
        flash(f"{successful_adds}/{len(form.bulk_users.data)} users were successfully added.", 'success')
        return redirect(url_for('hours.manage_hours'))

    return render_template('add_bulk_users.html', form=form)
