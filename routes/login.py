from flask import render_template, redirect, url_for, request, session
from helpers import flashes
from helpers.decorators import login_required
from helpers.forms import (
    get_date_of_birth,
    get_gender,
    get_zip_code,
    get_admin_status,
    get_max_date_of_birth
)
from helpers.validators import (
    username_too_short,
    username_too_long,
    password_too_short,
    invalid_optional_date,
    invalid_zip_code
)
from app import app
from data import users

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("browse_news"))

    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        max_date = get_max_date_of_birth()
        return render_template("register.html", max_date=max_date)

    form_valid = True
    username = request.form["username"]
    password = request.form["password"]
    date_of_birth = get_date_of_birth()
    zip_code = get_zip_code()
    gender = get_gender()
    admin = get_admin_status()

    if username_too_short(username):
        flashes.username_too_short()
        form_valid = False
    elif username_too_long(username):
        flashes.username_too_long()
        form_valid = False
    elif password_too_short(password):
        flashes.password_too_short()
        form_valid = False
    elif invalid_optional_date(date_of_birth):
        flashes.invalid_date()
        form_valid = False
    elif invalid_zip_code(zip_code):
        flashes.invalid_zip_code()
        form_valid = False

    if form_valid and users.register(username, password, date_of_birth, gender, zip_code, admin):
        users.login(username, password)
        return redirect("/")

    return render_template("register.html",
                            username=username,
                            password=password,
                            date_of_birth=date_of_birth,
                            gender=gender,
                            zip_code=zip_code,
                            admin="yes" if admin else "no")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    response = users.login(username, password)

    if response == "success":
        return redirect(url_for("browse_news"))

    if response == "account-disabled":
        flashes.account_disabled()
    else:
        flashes.invalid_credentials()

    return render_template("index.html", username=username, password=password)

@app.route("/logout")
@login_required
def logout():
    users.logout()
    return redirect("/")
