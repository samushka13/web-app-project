from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import flash, render_template, redirect, url_for, request
from app import app
from helpers.contants import DATE_LENGTH, TITLE_MIN_LENGTH, TITLE_MAX_LENGTH, ZIP_CODE_LENGTH
from helpers.decorators import login_required, admin_required
from helpers.forms import csrf_check_passed, get_date, get_zip_code
from data import polls

def redirect_to_polls():
    return redirect(url_for("browse_polls"))

def render_polls_template(poll_list):
    return render_template("browse_polls.html", polls=poll_list)

def render_poll_template(poll_id):
    return redirect(url_for("view_poll_details", poll_id=poll_id))

@app.route("/browse_polls")
@login_required
def browse_polls():
    poll_list = polls.get_current()
    return render_polls_template(poll_list)

@app.route("/browse_polls/upcoming")
@login_required
def browse_upcoming_polls():
    poll_list = polls.get_upcoming()
    return render_polls_template(poll_list)

@app.route("/browse_polls/past")
@login_required
def browse_past_polls():
    poll_list = polls.get_past()
    return render_polls_template(poll_list)

@app.route("/browse_polls/archived")
@admin_required
def browse_archived_polls():
    poll_list = polls.get_archived()
    return render_polls_template(poll_list)

@app.route("/browse_polls/nearby")
@login_required
def browse_nearby_polls():
    poll_list = polls.get_nearby()
    return render_polls_template(poll_list)

@app.route("/browse_polls/details/<int:poll_id>")
@login_required
def view_poll_details(poll_id):
    poll = polls.get_details(poll_id)

    if poll:
        return render_template("poll_details.html", poll=poll)

    flash("Tietojen haku epäonnistui", "error")
    return redirect_to_polls()

@app.route("/browse_polls/details/<int:poll_id>/analytics")
@login_required
def view_poll_analytics(poll_id):
    poll_title = polls.get_poll_title(poll_id)
    votes_by_gender = polls.get_votes_by_gender(poll_id)
    votes_by_age_group = polls.get_votes_by_age_group(poll_id)
    votes_by_zip_code = polls.get_votes_by_zip_code(poll_id)

    if poll_title and votes_by_gender and votes_by_age_group and votes_by_zip_code:
        return render_template("poll_analytics.html",
                                poll_id=poll_id,
                                poll_title=poll_title,
                                votes_by_gender=votes_by_gender,
                                votes_by_age_group=votes_by_age_group,
                                votes_by_zip_code=votes_by_zip_code)

    flash("Tietojen haku epäonnistui", "error")
    return render_poll_template(poll_id)

@app.route("/vote_for/<int:poll_id>", methods=["POST"])
@login_required
def vote_for(poll_id):
    if not (csrf_check_passed() and polls.vote(poll_id, True)):
        flash("Äänestäminen epäonnistui", "error")

    return render_poll_template(poll_id)

@app.route("/vote_against/<int:poll_id>", methods=["POST"])
@login_required
def vote_against(poll_id):
    if not (csrf_check_passed() and polls.vote(poll_id, False)):
        flash("Äänestäminen epäonnistui", "error")

    return render_poll_template(poll_id)

@app.route("/add_poll", methods=["GET", "POST"])
@admin_required
def add_poll():
    if request.method == "GET":
        current_date = datetime.today().date()
        future_date = current_date + relativedelta(months=+1)
        return render_template("add_poll.html", current_date=current_date, future_date=future_date)

    form_valid = csrf_check_passed()
    title = request.form["title"]
    zip_code = get_zip_code()
    open_on = get_date("open_on")
    close_on = get_date("close_on")

    if len(title) < TITLE_MIN_LENGTH:
        flash("Otsikko ei saa olla tyhjä", "error")
        form_valid = False
    elif len(title) > TITLE_MAX_LENGTH:
        flash("Otsikossa voi olla enintään 100 merkkiä", "error")
        form_valid = False
    elif zip_code and (len(zip_code) != ZIP_CODE_LENGTH or not zip_code.isdigit()):
        flash("Postinumerossa tulee olla 5 numeroa", "error")
        form_valid = False
    elif not open_on or len(open_on) < DATE_LENGTH:
        flash("Alkamispäivämäärä ei ole kelvollinen", "error")
        form_valid = False
    elif not close_on or len(close_on) < DATE_LENGTH:
        flash("Päättymispäivämäärä ei ole kelvollinen", "error")
        form_valid = False
    elif datetime.strptime(open_on, "%Y-%m-%d") > datetime.strptime(close_on, "%Y-%m-%d"):
        flash("Alkamispäivämäärän on oltava ennen päättymispäivämäärää", "error")
        form_valid = False

    if form_valid and polls.add(title, zip_code, open_on, close_on):
        flash("Kyselyn tallennus onnistui")
        return redirect_to_polls()

    flash("Kyselyn tallennus ei onnistunut", "error")
    return render_template("add_poll.html",
                            title=title,
                            zip_code=zip_code,
                            open_on=open_on,
                            close_on=close_on)

@app.route("/archive_poll/<int:poll_id>", methods=["POST"])
@admin_required
def archive_poll(poll_id):
    if not (csrf_check_passed() and polls.archive(poll_id)):
        flash("Arkistointi ei onnistunut", "error")

    return redirect_to_polls()

@app.route("/unarchive_poll/<int:poll_id>", methods=["POST"])
@admin_required
def unarchive_poll(poll_id):
    if not (csrf_check_passed() and polls.unarchive(poll_id)):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect_to_polls()
