from flask import render_template, redirect, url_for, request
from app import app
from helpers import flashes
from helpers.decorators import login_required, admin_required
from helpers.forms import csrf_check_passed, get_body
from helpers.pagination import get_pagination_variables
from helpers.validators import title_too_long, no_title, body_too_long
from data import feedback

def redirect_to_feedbacks():
    if "referrer" in request.form:
        if "acknowledged" in request.form["referrer"]:
            return redirect(url_for("browse_acknowledged_feedback"))
        if "archived" in request.form["referrer"]:
            return redirect(url_for("browse_archived_feedback"))

    return redirect(url_for("browse_feedback"))

def render_feedbacks_template(idx, last_idx, count, count_on_next_idx, feedbacks):
    return render_template("browse_feedback.html",
                           idx=idx,
                           last_idx=last_idx,
                           count=count,
                           count_on_next_idx=count_on_next_idx,
                           feedbacks=feedbacks)

@app.route("/give_feedback", methods=["GET", "POST"])
@login_required
def give_feedback():
    if request.method == "GET":
        return render_template("give_feedback.html")

    form_valid = csrf_check_passed()
    title = request.form["title"]
    body = get_body()

    if no_title(title):
        flashes.no_title()
        form_valid = False
    elif title_too_long(title):
        flashes.title_too_long()
        form_valid = False
    elif body_too_long(body):
        flashes.body_too_long()
        form_valid = False

    if form_valid and feedback.send(title, body):
        flashes.feedback_sent()
        return redirect_to_feedbacks()

    flashes.feedback_send_error()
    return render_template("give_feedback.html", title=title, body=body)

@app.route("/browse_feedback")
@login_required
def browse_feedback():
    pagination_vars = get_pagination_variables(feedback.get_new_count())
    feedbacks = feedback.get_new(pagination_vars[0])
    return render_feedbacks_template(*pagination_vars, feedbacks)

@app.route("/browse_feedback/acknowledged")
@login_required
def browse_acknowledged_feedback():
    pagination_vars = get_pagination_variables(feedback.get_acknowledged_count())
    feedbacks = feedback.get_acknowledged(pagination_vars[0])
    return render_feedbacks_template(*pagination_vars, feedbacks)

@app.route("/browse_feedback/archived")
@admin_required
def browse_archived_feedback():
    pagination_vars = get_pagination_variables(feedback.get_archived_count())
    feedbacks = feedback.get_archived(pagination_vars[0])
    return render_feedbacks_template(*pagination_vars, feedbacks)

@app.route("/acknowledge_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def acknowledge_feedback(feedback_id):
    if csrf_check_passed() and feedback.acknowledge(feedback_id):
        flashes.acknowledged()
    else:
        flashes.acknowledging_error()

    return redirect_to_feedbacks()

@app.route("/unacknowledge_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def unacknowledge_feedback(feedback_id):
    if csrf_check_passed() and feedback.unacknowledge(feedback_id):
        flashes.unacknowledged()
    else:
        flashes.unacknowledging_error()

    return redirect_to_feedbacks()

@app.route("/archive_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def archive_feedback(feedback_id):
    if csrf_check_passed() and feedback.archive(feedback_id):
        flashes.archived()
    else:
        flashes.archiving_error()

    return redirect_to_feedbacks()

@app.route("/unarchive_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def unarchive_feedback(feedback_id):
    if csrf_check_passed() and feedback.unarchive(feedback_id):
        flashes.unarchived()
    else:
        flashes.unarchiving_error()

    return redirect_to_feedbacks()
