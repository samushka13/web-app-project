from flask import flash, render_template, redirect, request
from app import app
from decorators import login_required, admin_required
import users
import session

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

        is_admin = "is_admin" in request.form

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

@app.route("/logout")
@login_required
def logout():
    users.logout()
    return redirect("/")

@app.route("/delete_user")
@login_required
def delete_user():
    if users.delete_user():
        users.logout()
        return redirect("/")

    flash("Tilin poistaminen ei onnistunut", "error")
    return render_template("profile.html")

@app.route("/news")
@login_required
def news():
    return render_template("news.html")

@app.route("/notices")
@login_required
def notices():
    return render_template("notices.html")

@app.route("/polls")
@login_required
def polls():
    return render_template("polls.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/feedback")
@login_required
def feedback():
    return render_template("feedback.html")

@app.route("/add_notice")
@login_required
def add_notice():
    return render_template("add_notice.html")

@app.route("/add_news")
@admin_required
def add_news():
    return render_template("add_news.html")

@app.route("/add_poll")
@admin_required
def add_poll():
    return render_template("add_poll.html")

@app.route("/manage_users", methods=["GET", "POST"])
@admin_required
def manage_users():
    if request.method == "GET":
        user_list = users.get_users()
        return render_template("manage_users.html", users=user_list)

    if request.method == "POST":
        if session.is_csrf_token_valid() and "user_id" in request.form:
            user_id = request.form["user_id"]
            if not users.disable_user(user_id):
                flash("Tilin poistaminen käytöstä ei onnistunut", "error")

            updated_user_list = users.get_users()
            return render_template("manage_users.html", users=updated_user_list)
