from datetime import datetime
from dateutil.relativedelta import relativedelta
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
        elif len(zip_code) != 5:
            flash("Postinumerossa tulee olla 5 numeroa", "error")
            is_form_valid = False

        if "is_admin" not in request.form:
            is_admin = False
        else:
            is_admin = request.form["is_admin"] == "yes"

        if is_form_valid:
            if not users.register(username, password, date_of_birth, gender, zip_code, is_admin):
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

@app.route("/update_date_of_birth", methods=["POST"])
@login_required
def update_date_of_birth():
    date_of_birth = request.form["date_of_birth"]

    if date_of_birth == "":
        date_of_birth = None

    user_id = session["user_id"]
    valid_token = users.is_csrf_token_valid()
    data_updated = users.update_date_of_birth(user_id, date_of_birth)

    if not (user_id and valid_token and data_updated):
        flash("Tallennus ei onnistunut", "error")

    return redirect(url_for("profile"))

@app.route("/update_gender", methods=["POST"])
@login_required
def update_gender():
    gender = request.form["gender"]

    if gender == "":
        gender = None

    user_id = session["user_id"]
    valid_token = users.is_csrf_token_valid()
    data_updated = users.update_gender(user_id, gender)

    if not (user_id and valid_token and data_updated):
        flash("Tallennus ei onnistunut", "error")

    return redirect(url_for("profile"))

@app.route("/update_zip_code", methods=["POST"])
@login_required
def update_zip_code():
    zip_code = request.form["zip_code"]

    if zip_code == "":
        zip_code = None
    elif len(zip_code) != 5:
        flash("Postinumerossa tulee olla 5 numeroa", "error")
        return redirect(url_for("profile"))

    user_id = session["user_id"]
    valid_token = users.is_csrf_token_valid()
    data_updated = users.update_zip_code(user_id, zip_code)

    if not (user_id and valid_token and data_updated):
        flash("Tallennus ei onnistunut", "error")

    return redirect(url_for("profile"))

@app.route("/update_admin_status", methods=["POST"])
@login_required
def update_admin_status():
    if "is_admin" not in request.form:
        flash("Ylläpitäjän rooli ei voi olla tyhjä", "error")
        return render_template("profile.html")
    else:
        is_admin = request.form["is_admin"] == "yes"

    user_id = session["user_id"]
    valid_token = users.is_csrf_token_valid()
    data_updated = users.update_admin_status(user_id, is_admin)

    if not (user_id and valid_token and data_updated):
        flash("Tallennus ei onnistunut", "error")

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
    news_list = news.get_new()
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

@app.route("/browse_notices/archived")
@admin_required
def browse_archived_notices():
    notice_list = notices.get_archived()
    return render_template("browse_notices.html", notices=notice_list)

@app.route("/browse_polls")
@login_required
def browse_polls():
    poll_list = polls.get_current()
    return render_template("browse_polls.html", polls=poll_list)

@app.route("/browse_polls/upcoming")
@login_required
def browse_upcoming_polls():
    poll_list = polls.get_upcoming()
    return render_template("browse_polls.html", polls=poll_list)

@app.route("/browse_polls/past")
@login_required
def browse_past_polls():
    poll_list = polls.get_past()
    return render_template("browse_polls.html", polls=poll_list)

@app.route("/browse_polls/archived")
@admin_required
def browse_archived_polls():
    poll_list = polls.get_archived()
    return render_template("browse_polls.html", polls=poll_list)

@app.route("/profile")
@login_required
def profile():
    current_date = datetime.today().date()
    max_date = current_date - relativedelta(years=18)
    return render_template("profile.html", max_date=max_date)

@app.route("/give_feedback", methods=["GET", "POST"])
@login_required
def give_feedback():
    if request.method == "GET":
        return render_template("give_feedback.html")

    if request.method == "POST":
        is_form_valid = True

        title = request.form["title"]

        if len(title) < 1:
            flash("Otsikko ei saa olla tyhjä", "error")
            is_form_valid = False

        if len(title) > 100:
            flash("Otsikossa voi olla enintään 100 merkkiä", "error")
            is_form_valid = False

        body = request.form["body"]

        if len(body) > 1000:
            flash("Kuvauksessa voi olla enintään 1000 merkkiä", "error")
            is_form_valid = False

        if body == "":
            body = None

        if is_form_valid:
            user_id = session["user_id"]
            token_valid = users.is_csrf_token_valid()
            data_updated = feedback.send(user_id, title, body)

            if not (user_id and token_valid and data_updated):
                flash("Palautteen lähetys ei onnistunut", "error")
            else:
                return redirect(url_for("browse_feedback"))

        return render_template("give_feedback.html", title=title, body=body)

@app.route("/add_notice", methods=["GET", "POST"])
@login_required
def add_notice():
    if request.method == "GET":
        return render_template("add_notice.html")

    if request.method == "POST":
        is_form_valid = True

        title = request.form["title"]

        if len(title) < 1:
            flash("Otsikko ei saa olla tyhjä", "error")
            is_form_valid = False

        if len(title) > 100:
            flash("Otsikossa voi olla enintään 100 merkkiä", "error")
            is_form_valid = False

        body = request.form["body"]

        if len(body) > 1000:
            flash("Lisätiedoissa voi olla enintään 1000 merkkiä", "error")
            is_form_valid = False

        if body == "":
            body = None

        zip_code = request.form["zip_code"]

        if zip_code == "":
            zip_code = None
        elif len(zip_code) != 5:
            flash("Postinumerossa tulee olla 5 numeroa", "error")
            is_form_valid = False

        street_address = request.form["street_address"]

        if street_address == "":
            street_address = None

        if is_form_valid:
            user_id = session["user_id"]
            token_valid = users.is_csrf_token_valid()
            data_updated = notices.add(user_id, title, body, zip_code, street_address)

            if not (user_id and token_valid and data_updated):
                flash("Ilmoituksen tallennus ei onnistunut", "error")
            else:
                return redirect(url_for("browse_notices"))

        return render_template("add_notice.html",
                                title=title,
                                body=body,
                                zip_code=zip_code,
                                street_address=street_address)

@app.route("/archive_notice/<int:notice_id>", methods=["POST"])
@admin_required
def archive_notice(notice_id):
    user_id = session["user_id"]
    token_valid = users.is_csrf_token_valid()
    data_updated = notices.archive(user_id, notice_id)

    if not (user_id and token_valid and data_updated):
        flash("Arkistointi ei onnistunut", "error")

    return redirect(url_for("browse_notices"))

@app.route("/unarchive_notice/<int:notice_id>", methods=["POST"])
@admin_required
def unarchive_notice(notice_id):
    user_id = session["user_id"]
    token_valid = users.is_csrf_token_valid()
    data_updated = notices.unarchive(user_id, notice_id)

    if not (user_id and token_valid and data_updated):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect(url_for("browse_notices"))

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
        current_date = datetime.today().date()
        return render_template("add_news.html", current_date=current_date)

    if request.method == "POST":
        is_form_valid = True

        title = request.form["title"]

        if len(title) < 1:
            flash("Otsikko ei saa olla tyhjä", "error")
            is_form_valid = False

        if len(title) > 100:
            flash("Otsikossa voi olla enintään 100 merkkiä", "error")
            is_form_valid = False

        body = request.form["body"]

        if len(body) > 1000:
            flash("Lisätiedoissa voi olla enintään 1000 merkkiä", "error")
            is_form_valid = False

        if body == "":
            body = None

        zip_code = request.form["zip_code"]

        if zip_code == "":
            zip_code = None
        elif len(zip_code) != 5:
            flash("Postinumerossa tulee olla 5 numeroa", "error")
            is_form_valid = False

        publish_on = request.form["publish_on"]

        if publish_on == "":
            publish_on = None

        if is_form_valid:
            user_id = session["user_id"]
            token_valid = users.is_csrf_token_valid()
            data_updated = news.add(user_id, title, body, zip_code, publish_on)

            if not (user_id and token_valid and data_updated):
                flash("Uutisen tallennus ei onnistunut", "error")
            else:
                return redirect(url_for("browse_news"))

        return render_template("add_news.html",
                                title=title,
                                body=body,
                                zip_code=zip_code,
                                publish_on=publish_on)

@app.route("/archive_news/<int:news_id>", methods=["POST"])
@admin_required
def archive_news(news_id):
    user_id = session["user_id"]
    token_valid = users.is_csrf_token_valid()
    data_updated = news.archive(user_id, news_id)

    if not (user_id and token_valid and data_updated):
        flash("Arkistointi ei onnistunut", "error")

    return redirect(url_for("browse_news"))

@app.route("/unarchive_news/<int:news_id>", methods=["POST"])
@admin_required
def unarchive_news(news_id):
    user_id = session["user_id"]
    token_valid = users.is_csrf_token_valid()
    data_updated = news.unarchive(user_id, news_id)

    if not (user_id and token_valid and data_updated):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect(url_for("browse_news"))

@app.route("/add_poll", methods=["GET", "POST"])
@admin_required
def add_poll():
    if request.method == "GET":
        current_date = datetime.today().date()
        future_date = current_date + relativedelta(months=+1)
        return render_template("add_poll.html", current_date=current_date, future_date=future_date)

    if request.method == "POST":
        title = request.form["title"]
        zip_code = request.form["zip_code"]
        open_on = request.form["open_on"]
        close_on = request.form["close_on"]

        is_form_valid = True

        if len(title) < 1:
            flash("Otsikko ei saa olla tyhjä", "error")
            is_form_valid = False

        if len(title) > 100:
            flash("Otsikossa voi olla enintään 100 merkkiä", "error")
            is_form_valid = False

        if zip_code == "":
            zip_code = None
        elif len(zip_code) != 5:
            flash("Postinumerossa tulee olla 5 numeroa", "error")
            is_form_valid = False

        if open_on == "":
            flash("Alkamispäivämäärä ei saa olla tyhjä", "error")
            is_form_valid = False

        if close_on == "":
            flash("Päättymispäivämäärä ei saa olla tyhjä", "error")
            is_form_valid = False

        if datetime.strptime(open_on, "%Y-%m-%d") > datetime.strptime(close_on, "%Y-%m-%d"):
            flash("Alkamispäivämäärän on oltava ennen päättymispäivämäärää", "error")
            is_form_valid = False

        if is_form_valid:
            user_id = session["user_id"]
            token_valid = users.is_csrf_token_valid()
            data_updated = polls.add(user_id, title, zip_code, open_on, close_on)

            if not (user_id and token_valid and data_updated):
                flash("Kyselyn tallennus ei onnistunut", "error")
            else:
                return redirect(url_for("browse_polls"))

        return render_template("add_poll.html",
                                title=title,
                                zip_code=zip_code,
                                open_on=open_on,
                                close_on=close_on)

@app.route("/archive_poll/<int:poll_id>", methods=["POST"])
@admin_required
def archive_poll(poll_id):
    user_id = session["user_id"]
    token_valid = users.is_csrf_token_valid()
    data_updated = polls.archive(user_id, poll_id)

    if not (user_id and token_valid and data_updated):
        flash("Arkistointi ei onnistunut", "error")

    return redirect(url_for("browse_polls"))

@app.route("/unarchive_poll/<int:poll_id>", methods=["POST"])
@admin_required
def unarchive_poll(poll_id):
    user_id = session["user_id"]
    token_valid = users.is_csrf_token_valid()
    data_updated = polls.unarchive(user_id, poll_id)

    if not (user_id and token_valid and data_updated):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect(url_for("browse_polls"))

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
