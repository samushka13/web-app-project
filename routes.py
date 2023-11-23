from flask import flash, render_template, redirect, url_for, request, session
from app import app
from decorators import login_required, admin_required
import feedback
import news
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
        else:
            gender = request.form["gender"]

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
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        login_response = users.login(username, password)

        if login_response == "credential-error":
            flash("Kirjautuminen ei onnistunut (väärä käyttäjänimi tai salasana)", "error")

        if login_response == "account-disabled":
            flash("Tili on poistettu käytöstä.", "error")

    return redirect("/")

@app.route("/logout")
@login_required
def logout():
    users.logout()
    return redirect("/")

@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    if "gender" not in request.form:
        gender = session["gender"]
    else:
        gender = request.form["gender"]

    date_of_birth = request.form["date_of_birth"]

    if date_of_birth == "":
        date_of_birth = session["date_of_birth"]

    zip_code = request.form["zip_code"]

    if zip_code == "":
        zip_code = session["zip_code"]

    if "is_admin" not in request.form:
        is_admin = session["is_admin"]
    else:
        is_admin = request.form["is_admin"]

    user_id = session["user_id"]
    valid_token = users.is_csrf_token_valid()
    data_updated = users.update_profile(user_id, date_of_birth, gender, zip_code, is_admin)

    if not (user_id and valid_token and data_updated):
        flash("Tietojen päivitys ei onnistunut", "error")

    return redirect(url_for("profile"))

@app.route("/delete_current_user", methods=["POST"])
@login_required
def delete_current_user():
    if "user_id" in session:
        user_id = session["user_id"]

        if users.is_csrf_token_valid() and users.delete_user(user_id):
            users.logout()
            return redirect("/")

    flash("Tilin poistaminen ei onnistunut", "error")
    return render_template("profile.html")

@app.route("/browse_news")
@login_required
def browse_news():
    news_list = news.get_all()
    return render_template("browse_news.html", news=news_list)

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

@app.route("/give_feedback", methods=["GET", "POST"])
@login_required
def give_feedback():
    if request.method == "GET":
        return render_template("give_feedback.html")

    if request.method == "POST":
        title = request.form["title"]

        if len(title) < 1:
            flash("Otsikko ei saa olla tyhjä", "error")

        if len(title) > 100:
            flash("Otsikossa voi olla enintään 100 merkkiä", "error")

        body = request.form["body"]

        if len(body) > 1000:
            flash("Kuvauksessa voi olla enintään 1000 merkkiä", "error")

        if body == "":
            body = None

        user_id = session["user_id"]
        token_valid = users.is_csrf_token_valid()
        data_updated = feedback.send(user_id, title, body)

        if not (user_id and token_valid and data_updated):
            flash("Palautteen lähetys ei onnistunut", "error")
        else:
            flash("Palautteen lähetys onnistui")

        return redirect(url_for("give_feedback"))

@app.route("/add_notice")
@login_required
def add_notice():
    return render_template("add_notice.html")

@app.route("/add_news", methods=["GET", "POST"])
@admin_required
def add_news():
    if request.method == "GET":
        return render_template("add_news.html")

    if request.method == "POST":
        title = request.form["title"]

        if len(title) < 1:
            flash("Otsikko ei saa olla tyhjä", "error")

        if len(title) > 100:
            flash("Otsikossa voi olla enintään 100 merkkiä", "error")

        body = request.form["body"]

        if len(body) > 1000:
            flash("Lisätiedoissa voi olla enintään 1000 merkkiä", "error")

        if body == "":
            body = None

        zip_code = request.form["zip_code"]

        if zip_code == "":
            zip_code = None

        publish_on = request.form["publish_on"]

        if publish_on == "":
            publish_on = None

        user_id = session["user_id"]
        token_valid = users.is_csrf_token_valid()
        data_updated = news.add(user_id, title, body, zip_code, publish_on)

        if not (user_id and token_valid and data_updated):
            flash("Uutisen tallennus ei onnistunut", "error")
        else:
            flash("Uutisen tallennus onnistui")

        return redirect(url_for("add_news"))

@app.route("/add_poll")
@admin_required
def add_poll():
    return render_template("add_poll.html")

@app.route("/browse_feedback")
@admin_required
def browse_feedback():
    feedbacks = feedback.get_all()
    return render_template("browse_feedback.html", feedbacks=feedbacks)

@app.route("/manage_users", methods=["GET", "POST"])
@admin_required
def manage_users():
    if request.method == "GET":
        user_list = users.get_users()
        return render_template("manage_users.html", users=user_list)

    if request.method == "POST":
        if users.is_csrf_token_valid() and "user_id" in request.form:
            user_id = request.form["user_id"]
            if not users.disable_user(user_id):
                flash("Tilin poistaminen käytöstä ei onnistunut", "error")

        return redirect(url_for("manage_users"))
