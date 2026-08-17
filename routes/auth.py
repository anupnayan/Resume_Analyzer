from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from sqlalchemy import select

from extensions import db
from models import User


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if current_user.is_authenticated:
        return redirect(
            url_for("main.dashboard")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name:
            flash(
                "Name is required.",
                "danger"
            )
            return render_template(
                "auth/register.html"
            )

        if not email:
            flash(
                "Email is required.",
                "danger"
            )
            return render_template(
                "auth/register.html"
            )

        if "@" not in email:
            flash(
                "Enter a valid email address.",
                "danger"
            )
            return render_template(
                "auth/register.html"
            )

        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "danger"
            )
            return render_template(
                "auth/register.html"
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger"
            )
            return render_template(
                "auth/register.html"
            )

        existing_user = db.session.scalar(
            select(User).where(
                User.email == email
            )
        )

        if existing_user:

            flash(
                "An account with this email already exists.",
                "warning"
            )

            return render_template(
                "auth/register.html"
            )

        user = User(
            name=name,
            email=email
        )

        user.set_password(
            password
        )

        db.session.add(user)
        db.session.commit()

        login_user(
            user
        )

        flash(
            "Account created successfully.",
            "success"
        )

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "auth/register.html"
    )


@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:
        return redirect(
            url_for("main.dashboard")
        )

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = db.session.scalar(
            select(User).where(
                User.email == email
            )
        )

        if (
            user is None
            or not user.check_password(password)
        ):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        login_user(
            user
        )

        next_page = request.args.get(
            "next"
        )

        if (
            next_page
            and next_page.startswith("/")
        ):
            return redirect(next_page)

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "auth/login.html"
    )


@auth_bp.route(
    "/logout"
)
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("main.index")
    )