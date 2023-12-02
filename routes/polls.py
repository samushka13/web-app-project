from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import render_template, redirect, url_for, request
from app import app
from helpers import flashes
from helpers.decorators import login_required, admin_required
from helpers.forms import csrf_check_passed, get_date, get_zip_code
from helpers.pagination import get_pagination_variables
from helpers.validators import (
    invalid_required_date,
    no_title,
    title_too_long,
    invalid_zip_code,
    start_date_before_end_date
)
from data import polls

def redirect_to_polls():
    if "referrer" in request.form:
        if "nearby" in request.form["referrer"]:
            return redirect(url_for("browse_nearby_polls"))
        if "upcoming" in request.form["referrer"]:
            return redirect(url_for("browse_upcoming_polls"))
        if "past" in request.form["referrer"]:
            return redirect(url_for("browse_past_polls"))
        if "archived" in request.form["referrer"]:
            return redirect(url_for("browse_archived_polls"))

    return redirect(url_for("browse_polls"))

def render_polls_template(idx, last_idx, count, count_on_next_idx, poll_list):
    return render_template("browse_polls.html",
                           idx=idx,
                           last_idx=last_idx,
                           count=count,
                           count_on_next_idx=count_on_next_idx,
                           polls=poll_list)

def render_poll_template(poll_id):
    return redirect(url_for("view_poll_details", poll_id=poll_id))

@app.route("/browse_polls")
@login_required
def browse_polls():
    pagination_vars = get_pagination_variables(polls.get_current_count())
    poll_list = polls.get_current(pagination_vars[0])
    return render_polls_template(*pagination_vars, poll_list)

@app.route("/browse_polls/upcoming")
@login_required
def browse_upcoming_polls():
    pagination_vars = get_pagination_variables(polls.get_upcoming_count())
    poll_list = polls.get_upcoming(pagination_vars[0])
    return render_polls_template(*pagination_vars, poll_list)

@app.route("/browse_polls/past")
@login_required
def browse_past_polls():
    pagination_vars = get_pagination_variables(polls.get_past_count())
    poll_list = polls.get_past(pagination_vars[0])
    return render_polls_template(*pagination_vars, poll_list)

@app.route("/browse_polls/archived")
@admin_required
def browse_archived_polls():
    pagination_vars = get_pagination_variables(polls.get_archived_count())
    poll_list = polls.get_archived(pagination_vars[0])
    return render_polls_template(*pagination_vars, poll_list)

@app.route("/browse_polls/nearby")
@login_required
def browse_nearby_polls():
    pagination_vars = get_pagination_variables(polls.get_nearby_count())
    poll_list = polls.get_nearby(pagination_vars[0])
    return render_polls_template(*pagination_vars, poll_list)

@app.route("/browse_polls/details/<int:poll_id>")
@login_required
def view_poll_details(poll_id):
    poll = polls.get_details(poll_id)

    if poll:
        return render_template("poll_details.html", poll=poll)

    flashes.data_fetch_failed()
    return redirect_to_polls()

@app.route("/browse_polls/details/<int:poll_id>/analytics")
@login_required
def view_poll_analytics(poll_id):
    poll_title = polls.get_poll_title(poll_id)
    votes_by_gender = polls.get_votes_by_gender(poll_id)
    votes_by_age_group = polls.get_votes_by_age_group(poll_id)
    votes_by_zip_code = polls.get_votes_by_zip_code(poll_id)
    votes_for = sum(votes_by_gender[::2])
    votes_against = sum(votes_by_gender[1::2])

    if poll_title and votes_by_gender and votes_by_age_group and votes_by_zip_code:
        return render_template("poll_analytics.html",
                                poll_id=poll_id,
                                poll_title=poll_title,
                                votes_by_gender=votes_by_gender,
                                votes_by_age_group=votes_by_age_group,
                                votes_by_zip_code=votes_by_zip_code,
                                votes_for=votes_for,
                                votes_against=votes_against)

    flashes.data_fetch_failed()
    return render_poll_template(poll_id)

@app.route("/vote_for/<int:poll_id>", methods=["POST"])
@login_required
def vote_for(poll_id):
    if not (csrf_check_passed() and polls.vote(poll_id, True)):
        flashes.vote_error()

    return render_poll_template(poll_id)

@app.route("/vote_against/<int:poll_id>", methods=["POST"])
@login_required
def vote_against(poll_id):
    if not (csrf_check_passed() and polls.vote(poll_id, False)):
        flashes.vote_error()

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

    if no_title(title):
        flashes.no_title()
        form_valid = False
    elif title_too_long(title):
        flashes.title_too_long()
        form_valid = False
    elif invalid_zip_code(zip_code):
        flashes.invalid_zip_code()
        form_valid = False
    elif invalid_required_date(open_on):
        flashes.invalid_start_date()
        form_valid = False
    elif invalid_required_date(close_on):
        flashes.invalid_end_date()
        form_valid = False
    elif start_date_before_end_date(open_on, close_on):
        flashes.start_date_before_end_date()
        form_valid = False

    if form_valid and polls.add(title, zip_code, open_on, close_on):
        flashes.poll_saved()
        return redirect_to_polls()

    flashes.poll_save_error()
    return render_template("add_poll.html",
                            title=title,
                            zip_code=zip_code,
                            open_on=open_on,
                            close_on=close_on)

@app.route("/archive_poll/<int:poll_id>", methods=["POST"])
@admin_required
def archive_poll(poll_id):
    if csrf_check_passed() and polls.archive(poll_id):
        flashes.archived()
    else:
        flashes.archiving_error()

    return redirect_to_polls()

@app.route("/unarchive_poll/<int:poll_id>", methods=["POST"])
@admin_required
def unarchive_poll(poll_id):
    if csrf_check_passed() and polls.unarchive(poll_id):
        flashes.unarchived()
    else:
        flashes.unarchiving_error()

    return redirect_to_polls()
