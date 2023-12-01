from flask import render_template, redirect, url_for, request, session
from werkzeug.security import check_password_hash
from app import app
from helpers import flashes
from helpers.contants import GENDERS
from helpers.decorators import login_required
from helpers.forms import (
    csrf_check_passed,
    get_date_of_birth,
    get_gender,
    get_zip_code,
    get_admin_status,
    get_max_date_of_birth
)
from helpers.validators import password_too_short, invalid_optional_date, invalid_zip_code
from data import users

def redirect_to_profile():
    return redirect(url_for("profile"))

def handle_profile_update(update_success: bool):
    if csrf_check_passed() and update_success:
        flashes.profile_updated()
    else:
        flashes.profile_update_error()

@app.route("/profile")
@login_required
def profile():
    max_date = get_max_date_of_birth()
    return render_template("profile.html", max_date=max_date, genders=GENDERS)

@app.route("/update_date_of_birth", methods=["POST"])
@login_required
def update_date_of_birth():
    date_of_birth = get_date_of_birth()

    if invalid_optional_date(date_of_birth):
        flashes.invalid_date()
    else:
        handle_profile_update(users.update_date_of_birth(date_of_birth))

    return redirect_to_profile()

@app.route("/update_gender", methods=["POST"])
@login_required
def update_gender():
    gender = get_gender()

    handle_profile_update(users.update_gender(gender))

    return redirect_to_profile()

@app.route("/update_zip_code", methods=["POST"])
@login_required
def update_zip_code():
    zip_code = get_zip_code()

    if invalid_zip_code(zip_code):
        flashes.invalid_zip_code()
        return redirect_to_profile()
    else:
        handle_profile_update(users.update_zip_code(zip_code))

    return redirect_to_profile()

@app.route("/update_admin_status", methods=["POST"])
@login_required
def update_admin_status():
    admin = get_admin_status()

    handle_profile_update(users.update_admin_status(admin))

    return redirect_to_profile()

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "GET":
        return render_template("change_password.html")

    if "password_hash" in session:
        current = request.form["current"]
        new = request.form["new"]
        password_match = check_password_hash(session["password_hash"], current)

        if not password_match:
            flashes.password_mismatch()
        elif password_too_short(new):
            flashes.password_too_short()
        elif csrf_check_passed() and users.change_password(new):
            flashes.password_changed()
            return redirect_to_profile()

    flashes.password_change_error()
    return render_template("change_password.html", current=current, new=new)

@app.route("/delete_current_user", methods=["POST"])
@login_required
def delete_current_user():
    if csrf_check_passed() and users.delete_current_user():
        users.logout()
        flashes.profile_updated()
        return redirect("/")

    flashes.profile_update_error()
    return render_template("profile.html")
