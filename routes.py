from flask import flash, render_template, redirect, request
from app import app
import users

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]

        if len(username) < 6:
            flash("Käyttäjänimessä tulee olla vähintään 6 merkkiä", "error")
            return render_template("register.html")

        if len(username) > 50:
            flash("Käyttäjänimessä voi olla enintään 50 merkkiä", "error")
            return render_template("register.html")

        password = request.form["password"]

        if len(password) < 6:
            flash("Salasanassa tulee olla vähintään 6 merkkiä", "error")
            return render_template("register.html")

        if "gender" not in request.form:
            gender = None

        date_of_birth = request.form["date_of_birth"]

        if date_of_birth == "":
            date_of_birth = None

        zip_code = request.form["zip_code"]

        if zip_code == "":
            zip_code = None

        if "is_admin" not in request.form:
            is_admin = False

        if not users.register(username, password, date_of_birth, gender, zip_code, is_admin):
            flash("Rekisteröityminen ei onnistunut", "error")
            return render_template("register.html")

        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not users.login(username, password):
            flash("Kirjautuminen ei onnistunut (väärä käyttäjänimi tai salasana)", "error")
            return render_template("login.html")

        return redirect("/")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/notices")
def notices():
    return render_template("notices.html")

@app.route("/polls")
def polls():
    return render_template("polls.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/add_news")
def add_news():
    return render_template("add_news.html")

@app.route("/add_notice")
def add_notice():
    return render_template("add_notice.html")

@app.route("/add_poll")
def add_poll():
    return render_template("add_poll.html")

@app.route("/registered_users")
def registered_users():
    return render_template("registered_users.html")
