from datetime import datetime
from flask import flash, render_template, redirect, url_for, request, session
from app import app
from decorators import login_required, admin_required
import feedback
import news
import notices
import polls
import users

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("browse_news"))

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
        elif 0 < len(zip_code) < 5:
            flash("Postinumerossa tulee olla 5 numeroa", "error")

        if "is_admin" not in request.form:
            is_admin = False
        else:
            is_admin = request.form["is_admin"] == "yes"

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

    return redirect(url_for("browse_news"))

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
        if session["date_of_birth"]:
            date_of_birth = datetime.strptime(str(session["date_of_birth"]), '%d.%m.%Y')
        else:
            date_of_birth = None

    zip_code = request.form["zip_code"]

    if zip_code == "":
        zip_code = session["zip_code"]
    elif 0 < len(zip_code) < 5:
        flash("Postinumerossa tulee olla 5 numeroa", "error")

    if "is_admin" not in request.form:
        is_admin = session["is_admin"]
    else:
        is_admin = request.form["is_admin"] == "yes"

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

@app.route("/browse_news/archived")
@admin_required
def browse_archived_news():
    news_list = news.get_archived()
    return render_template("browse_news.html", news=news_list)

@app.route("/browse_news/upcoming")
@admin_required
def browse_upcoming_news():
    news_list = news.get_upcoming()
    return render_template("browse_news.html", news=news_list)

@app.route("/browse_notices")
@login_required
def browse_notices():
    notice_list = notices.get_all()
    return render_template("browse_notices.html", notices=notice_list)

@app.route("/browse_notices/my")
@login_required
def browse_my_notices():
    notice_list = []

    if "user_id" in session:
        user_id = session["user_id"]
        notice_list = notices.get_user_notices(user_id)

    return render_template("browse_notices.html", notices=notice_list)

@app.route("/browse_polls")
@login_required
def browse_polls():
    poll_list = polls.get_all()
    return render_template("browse_polls.html", polls=poll_list)

@app.route("/profile")
@login_required
def profile():
    gender = "-"

    if session["gender"] == "female":
        gender = "nainen"
    elif session["gender"] == "male":
        gender = "mies"
    elif session["gender"] == "other":
        gender = "muu"

    is_admin = "ei"

    if session["is_admin"] is True:
        is_admin = "kyllä"

    return render_template("profile.html", gender=gender, is_admin=is_admin)

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
            return redirect(url_for("browse_feedback"))

        return render_template("give_feedback.html")

@app.route("/add_notice", methods=["GET", "POST"])
@login_required
def add_notice():
    if request.method == "GET":
        return render_template("add_notice.html")

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
        elif 0 < len(zip_code) < 5:
            flash("Postinumerossa tulee olla 5 numeroa", "error")

        street_address = request.form["street_address"]

        if street_address == "":
            street_address = None

        user_id = session["user_id"]
        token_valid = users.is_csrf_token_valid()
        data_updated = notices.add(user_id, title, body, zip_code, street_address)

        if not (user_id and token_valid and data_updated):
            flash("Ilmoituksen tallennus ei onnistunut", "error")
        else:
            return redirect(url_for("browse_notices"))

        return render_template("add_notice.html")

@app.route("/browse_feedback")
@login_required
def browse_feedback():
    feedbacks = feedback.get_new()
    return render_template("browse_feedback.html", feedbacks=feedbacks)

@app.route("/browse_feedback/acknowledged")
@login_required
def browse_acknowledged_feedback():
    feedbacks = feedback.get_acknowledged()
    return render_template("browse_feedback.html", feedbacks=feedbacks)

@app.route("/browse_feedback/archived")
@admin_required
def browse_archived_feedback():
    feedbacks = feedback.get_archived()
    return render_template("browse_feedback.html", feedbacks=feedbacks)

@app.route("/acknowledge_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def acknowledge_feedback(feedback_id):
    user_id = session["user_id"]
    token_valid = users.is_csrf_token_valid()
    data_updated = feedback.acknowledge(user_id, feedback_id)

    if not (user_id and token_valid and data_updated):
        flash("Huomioiduksi merkitseminen ei onnistunut", "error")

    return redirect(url_for("browse_feedback"))

@app.route("/unacknowledge_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def unacknowledge_feedback(feedback_id):
    user_id = session["user_id"]
    token_valid = users.is_csrf_token_valid()
    data_updated = feedback.unacknowledge(user_id, feedback_id)

    if not (user_id and token_valid and data_updated):
        flash("Huomioinnin peruminen ei onnistunut", "error")

    return redirect(url_for("browse_feedback"))

@app.route("/archive_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def archive_feedback(feedback_id):
    user_id = session["user_id"]
    token_valid = users.is_csrf_token_valid()
    data_updated = feedback.archive(user_id, feedback_id)

    if not (user_id and token_valid and data_updated):
        flash("Arkistointi ei onnistunut", "error")

    return redirect(url_for("browse_feedback"))

@app.route("/unarchive_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def unarchive_feedback(feedback_id):
    user_id = session["user_id"]
    token_valid = users.is_csrf_token_valid()
    data_updated = feedback.unarchive(user_id, feedback_id)

    if not (user_id and token_valid and data_updated):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect(url_for("browse_feedback"))

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
        elif 0 < len(zip_code) < 5:
            flash("Postinumerossa tulee olla 5 numeroa", "error")

        publish_on = request.form["publish_on"]

        if publish_on == "":
            publish_on = None

        user_id = session["user_id"]
        token_valid = users.is_csrf_token_valid()
        data_updated = news.add(user_id, title, body, zip_code, publish_on)

        if not (user_id and token_valid and data_updated):
            flash("Uutisen tallennus ei onnistunut", "error")
        else:
            return redirect(url_for("browse_news"))

        return render_template("add_news.html")

@app.route("/add_poll", methods=["GET", "POST"])
@admin_required
def add_poll():
    if request.method == "GET":
        return render_template("add_poll.html")

    if request.method == "POST":
        title = request.form["title"]

        if len(title) < 1:
            flash("Otsikko ei saa olla tyhjä", "error")

        if len(title) > 100:
            flash("Otsikossa voi olla enintään 100 merkkiä", "error")

        zip_code = request.form["zip_code"]

        if zip_code == "":
            zip_code = None
        elif 0 < len(zip_code) < 5:
            flash("Postinumerossa tulee olla 5 numeroa", "error")

        open_on = request.form["open_on"]

        if open_on == "":
            flash("Alkamispäivämäärä ei saa olla tyhjä", "error")

        close_on = request.form["close_on"]

        if close_on == "":
            flash("Päättymispäivämäärä ei saa olla tyhjä", "error")

        user_id = session["user_id"]
        token_valid = users.is_csrf_token_valid()
        data_updated = polls.add(user_id, title, zip_code, open_on, close_on)

        if not (user_id and token_valid and data_updated):
            flash("Kyselyn tallennus ei onnistunut", "error")
        else:
            return redirect(url_for("browse_polls"))

        return render_template("add_poll.html")

@app.route("/manage_users")
@admin_required
def manage_users():
    user_list = users.get_users()
    return render_template("manage_users.html", users=user_list)

@app.route("/disable_user/<int:user_id>", methods=["POST"])
@admin_required
def disable_user(user_id):
    if not (users.is_csrf_token_valid() and users.disable_user(user_id)):
        flash("Tilin poistaminen käytöstä ei onnistunut", "error")

    return redirect(url_for("manage_users"))

@app.route("/enable_user/<int:user_id>", methods=["POST"])
@admin_required
def enable_user(user_id):
    if not (users.is_csrf_token_valid() and users.enable_user(user_id)):
        flash("Tilin ottaminen käyttöön ei onnistunut", "error")

    return redirect(url_for("manage_users"))
