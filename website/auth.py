from flask import Blueprint, redirect, render_template, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import Notes, User, Profile
from . import db

auth = Blueprint('auth', __name__)


# Logging in the user
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user=User.query.filter_by(username=username).first(), remember=True)

                return redirect(url_for('views.main'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash("Username does not exist, try registering an account!", category='error')
    return render_template("login.html", user=current_user)


# Logging out the user
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# Registering the user
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists!", category='error')
        elif password1 != password2:
            flash("Passwords must match!", category='error')
        elif len(username) > 24:
            flash("Username is over 24 chars!", category='error')
        elif len(username) < 2:
            flash("Username to short!", category='error')
        else:
            new_user = User(username=username,
                            password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()

            user = User.query.filter_by(username=username).first()
            assert user.is_active
            login_user(user, remember=True)

            defualt_profile = Profile(pfp='https://i.imgur.com/eNsgEu8.png',
                                      about_me="Your 'About Me' page, write something about yourself!",
                                      user_id=current_user.id)  # sets up their default profile
            db.session.add(defualt_profile)
            db.session.commit()

            flash("Successfully created account!", category='success')  # auto logins btw

            return redirect(url_for('views.main'))

    return render_template("register.html", user=current_user)
