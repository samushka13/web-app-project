from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import flash, render_template, redirect, url_for, request, session
from helpers.contants import MIN_USER_AGE
from helpers.decorators import login_required
from helpers.forms import get_date_of_birth, get_gender, get_zip_code, get_admin_status
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
        max_date = current_date - relativedelta(years=MIN_USER_AGE)
        return render_template("register.html", max_date=max_date)

    is_form_valid = True
    username = request.form["username"]
    password = request.form["password"]
    date_of_birth = get_date_of_birth()
    zip_code = get_zip_code()
    gender = get_gender()
    is_admin = get_admin_status()

    if len(username) < 6:
        flash("Käyttäjänimessä tulee olla vähintään 6 merkkiä", "error")
        is_form_valid = False
    elif len(username) > 50:
        flash("Käyttäjänimessä voi olla enintään 50 merkkiä", "error")
        is_form_valid = False
    elif len(password) < 6:
        flash("Salasanassa tulee olla vähintään 6 merkkiä", "error")
        is_form_valid = False
    elif date_of_birth and len(date_of_birth) < 10:
        flash("Päivämäärä ei ole kelvollinen", "error")
        is_form_valid = False
    elif zip_code and len(zip_code) != 5:
        flash("Postinumerossa tulee olla 5 numeroa", "error")
        is_form_valid = False

    if is_form_valid:
        response = users.register(username, password, date_of_birth, gender, zip_code, is_admin)

        if response is True:
            return redirect("/")

        if response == "username-exists":
            flash("Käyttäjänimi on varattu", "error")
        else:
            flash("Rekisteröityminen ei onnistunut", "error")

    return render_template("register.html",
                            username=username,
                            password=password,
                            date_of_birth=date_of_birth,
                            gender=gender,
                            zip_code=zip_code,
                            is_admin="yes" if is_admin else "no")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    response = users.login(username, password)

    if response is True:
        return redirect(url_for("browse_news"))

    if response == "credential-error":
        flash("Väärä käyttäjänimi tai salasana", "error")
    elif response == "account-disabled":
        flash("Tili on poistettu käytöstä", "error")
    else:
        flash("Kirjautuminen ei onnistunut", "error")

    return render_template("index.html", username=username, password=password)

@app.route("/logout")
@login_required
def logout():
    users.logout()
    return redirect("/")
