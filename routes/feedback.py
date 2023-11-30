from flask import flash, render_template, redirect, url_for, request
from app import app
from helpers.decorators import login_required, admin_required
from helpers.csrf import is_csrf_token_valid
from data import feedback

def redirect_to_feedbacks():
    return redirect(url_for("browse_feedback"))

def render_feedback_template(feedbacks):
    if feedbacks is False:
        feedbacks = []
        flash("Palautteiden haku epäonnistui", "error")

    return render_template("browse_feedback.html", feedbacks=feedbacks)

@app.route("/give_feedback", methods=["GET", "POST"])
@login_required
def give_feedback():
    if request.method == "GET":
        return render_template("give_feedback.html")

    is_form_valid = is_csrf_token_valid()
    title = request.form["title"]
    body = request.form["body"]

    if len(title) < 1:
        flash("Otsikko ei saa olla tyhjä", "error")
        is_form_valid = False
    elif len(title) > 100:
        flash("Otsikossa voi olla enintään 100 merkkiä", "error")
        is_form_valid = False

    if body == "":
        body = None
    elif len(body) > 1000:
        flash("Kuvauksessa voi olla enintään 1000 merkkiä", "error")
        is_form_valid = False

    if is_form_valid and feedback.send(title, body):
        flash("Palautteen lähettäminen onnistui")
        return redirect_to_feedbacks()

    flash("Palautteen lähettäminen ei onnistunut", "error")
    return render_template("give_feedback.html", title=title, body=body)

@app.route("/browse_feedback")
@login_required
def browse_feedback():
    feedbacks = feedback.get_new()
    return render_feedback_template(feedbacks)

@app.route("/browse_feedback/acknowledged")
@login_required
def browse_acknowledged_feedback():
    feedbacks = feedback.get_acknowledged()
    return render_feedback_template(feedbacks)

@app.route("/browse_feedback/archived")
@admin_required
def browse_archived_feedback():
    feedbacks = feedback.get_archived()
    return render_feedback_template(feedbacks)

@app.route("/acknowledge_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def acknowledge_feedback(feedback_id):
    if not (is_csrf_token_valid() and feedback.acknowledge(feedback_id)):
        flash("Huomioiduksi merkitseminen ei onnistunut", "error")

    return redirect_to_feedbacks()

@app.route("/unacknowledge_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def unacknowledge_feedback(feedback_id):
    if not (is_csrf_token_valid() and feedback.unacknowledge(feedback_id)):
        flash("Huomioinnin peruminen ei onnistunut", "error")

    return redirect_to_feedbacks()

@app.route("/archive_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def archive_feedback(feedback_id):
    if not (is_csrf_token_valid() and feedback.archive(feedback_id)):
        flash("Arkistointi ei onnistunut", "error")

    return redirect_to_feedbacks()

@app.route("/unarchive_feedback/<int:feedback_id>", methods=["POST"])
@admin_required
def unarchive_feedback(feedback_id):
    if not (is_csrf_token_valid() and feedback.unarchive(feedback_id)):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect_to_feedbacks()
