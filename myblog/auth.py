import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from myblog.db import get_db

from myblog.form import LoginForm, RegistrationForm, ForgotForm

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Register a new user.

    Validates that the username or email are not already taken. Hashes the
    password for security.
    """
    form = RegistrationForm(request.form, meta={'csrf_context': session})
    if request.method == "POST" and form.validate():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        elif (
            db.execute("SELECT id FROM user WHERE username = ?", (username,)).fetchone()
            is not None
        ):
            error = f"User {username} is already registered."
        elif (
            db.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone()
            is not None
        ):
            error = f"Email {email} is already registered."

        if error is None:
            # the name and email is available, store it in the database and go to
            # the login page

            """
            Here the salting technique is used to hash the password using 
            the method pbkdf2:sha256 with salt length = 8 that is the default 
            values of the werkzeug.security.generate_password_hash method 
            as you can see in https://werkzeug.palletsprojects.com/en/1.0.x/utils/
            """
            db.execute(
                "INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                (username, email, generate_password_hash(password)),
            )
            db.commit()
            return redirect(url_for("auth.login"))

        flash(error)
    elif request.method == "POST" and not form.validate():
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, field_name.capitalize())

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Login a registered user by adding the user id to the session."""
    form = LoginForm(request.form, meta={'csrf_context': session})
    if request.method == "POST" and form.validate():
        username = form.username.data
        password = form.password.data
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            # store the user id in a new session and return to the index
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html", form=form)


@bp.route("/forgot", methods=("GET", "POST"))
def forgot():
    """Send an email if the user has forgotten the password or username by adding a registed email."""
    form = ForgotForm(request.form, meta={'csrf_context': session})
    if request.method == "POST" and form.validate():
        email = form.email.data
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM user WHERE email = ?", (email,)
        ).fetchone()

        if user is None:
            error = f"The email {email} is not registered."

        if error is None:
            # create new session, send email to recover credentials and return to the index
            session.clear()

            # here the code to send recover email ....
            print("\t \t Sending recovery email.....")

            return redirect(url_for("index"))

        flash(error)
    elif request.method == "POST" and not form.validate():
        for field_name, field_errors in form.errors.items():
            for error in field_errors:
                flash(error, field_name.capitalize())

    return render_template("auth/forgot.html", form=form)


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return redirect(url_for("index"))
