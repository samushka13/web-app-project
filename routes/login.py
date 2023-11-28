from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import flash, render_template, redirect, url_for, request, session
from helpers.decorators import login_required
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
        current_date = datetime.today().date()
        max_date = current_date - relativedelta(years=18)
        return render_template("register.html", max_date=max_date)

    if request.method == "POST":
        is_form_valid = True

        username = request.form["username"]
        password = request.form["password"]

        if len(username) < 6:
            flash("Käyttäjänimessä tulee olla vähintään 6 merkkiä", "error")
            is_form_valid = False

        if len(username) > 50:
            flash("Käyttäjänimessä voi olla enintään 50 merkkiä", "error")
            is_form_valid = False

        if len(password) < 6:
            flash("Salasanassa tulee olla vähintään 6 merkkiä", "error")
            is_form_valid = False

        if "gender" not in request.form or request.form["gender"] == "":
            gender = None
        else:
            gender = request.form["gender"]

        date_of_birth = request.form["date_of_birth"]

        if date_of_birth == "":
            date_of_birth = None

        zip_code = request.form["zip_code"]

        if zip_code == "":
            zip_code = None
        elif len(zip_code) != 5:
            flash("Postinumerossa tulee olla 5 numeroa", "error")
            is_form_valid = False

        if "is_admin" not in request.form:
            is_admin = False
        else:
            is_admin = request.form["is_admin"] == "yes"

        if is_form_valid:
            response = users.register(username, password, date_of_birth, gender, zip_code, is_admin)

            if response == "username-exists":
                flash("Käyttäjänimi on varattu", "error")
            elif not response:
                flash("Rekisteröityminen ei onnistunut", "error")
            else:
                return redirect("/")

        return render_template("register.html",
                                username=username,
                                password=password,
                                date_of_birth=date_of_birth,
                                gender=gender,
                                zip_code=zip_code,
                                is_admin="yes" if is_admin else "no")

@app.route("/login", methods=["POST"])
def login():
    is_form_valid = True

    username = request.form["username"]
    password = request.form["password"]

    login_response = users.login(username, password)

    if not login_response:
        flash("Kirjautuminen ei onnistunut", "error")
        is_form_valid = False

    if login_response == "credential-error":
        flash("Väärä käyttäjänimi tai salasana", "error")
        is_form_valid = False

    if login_response == "account-disabled":
        flash("Tili on poistettu käytöstä", "error")
        is_form_valid = False

    if is_form_valid:
        return redirect(url_for("browse_news"))

    return render_template("index.html", username=username, password=password)

@app.route("/logout")
@login_required
def logout():
    users.logout()
    return redirect("/")
