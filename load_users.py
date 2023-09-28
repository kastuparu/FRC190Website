from website import app, db, bcrypt
from website.models import User


if __name__ == '__main__':
    with app.app_context():
        new_users = open('website/static/account_info.csv', 'r')
        hashed_pw = bcrypt.generate_password_hash('password')
        for line in new_users:
            first_name, last_name, email, position = line.rstrip('\n').split(',')
            if not User.query.filter_by(email=email).first():
                user = User(email=email, password=hashed_pw, first_name=first_name,     # type: ignore[call-arg]
                            last_name=last_name, position=position,                     # type: ignore[call-arg]
                            profile_pic_filename='default.png', admin=False)            # type: ignore[call-arg]
                db.session.add(user)
                db.session.commit()
