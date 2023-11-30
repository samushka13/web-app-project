from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import flash, render_template, redirect, url_for, request
from app import app
from helpers.decorators import login_required, admin_required
from helpers.csrf import is_csrf_token_valid
from data import polls

def redirect_to_polls():
    return redirect(url_for("browse_polls"))

def render_polls_template(poll_list):
    if poll_list is False:
        poll_list = []
        flash("Ilmoitusten haku epäonnistui", "error")

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
    if not (is_csrf_token_valid() and polls.vote(poll_id, True)):
        flash("Äänestäminen epäonnistui", "error")

    if polls.get_details(poll_id):
        return render_poll_template(poll_id)

    flash("Tietojen haku epäonnistui", "error")
    return redirect_to_polls()

@app.route("/vote_against/<int:poll_id>", methods=["POST"])
@login_required
def vote_against(poll_id):
    if not (is_csrf_token_valid() and polls.vote(poll_id, False)):
        flash("Äänestäminen epäonnistui", "error")

    if polls.get_details(poll_id):
        return render_poll_template(poll_id)

    flash("Tietojen haku epäonnistui", "error")
    return redirect_to_polls()

@app.route("/add_poll", methods=["GET", "POST"])
@admin_required
def add_poll():
    if request.method == "GET":
        current_date = datetime.today().date()
        future_date = current_date + relativedelta(months=+1)
        return render_template("add_poll.html", current_date=current_date, future_date=future_date)

    is_form_valid = is_csrf_token_valid()
    title = request.form["title"]
    zip_code = request.form["zip_code"]
    open_on = request.form["open_on"]
    close_on = request.form["close_on"]

    if len(title) < 1:
        flash("Otsikko ei saa olla tyhjä", "error")
        is_form_valid = False
    elif len(title) > 100:
        flash("Otsikossa voi olla enintään 100 merkkiä", "error")
        is_form_valid = False

    if zip_code == "":
        zip_code = None
    elif len(zip_code) != 5:
        flash("Postinumerossa tulee olla 5 numeroa", "error")
        is_form_valid = False

    if not open_on or len(open_on) < 10:
        flash("Alkamispäivämäärä ei ole kelvollinen", "error")
        is_form_valid = False

    if not close_on or len(close_on) < 10:
        flash("Päättymispäivämäärä ei ole kelvollinen", "error")
        is_form_valid = False

    if datetime.strptime(open_on, "%Y-%m-%d") > datetime.strptime(close_on, "%Y-%m-%d"):
        flash("Alkamispäivämäärän on oltava ennen päättymispäivämäärää", "error")
        is_form_valid = False

    if is_form_valid and polls.add(title, zip_code, open_on, close_on):
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
    if not (is_csrf_token_valid() and polls.archive(poll_id)):
        flash("Arkistointi ei onnistunut", "error")

    return redirect_to_polls()

@app.route("/unarchive_poll/<int:poll_id>", methods=["POST"])
@admin_required
def unarchive_poll(poll_id):
    if not (is_csrf_token_valid() and polls.unarchive(poll_id)):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect_to_polls()
