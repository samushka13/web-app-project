from flask import flash, render_template, redirect, url_for, request
from app import app
from helpers.decorators import login_required, admin_required
from helpers.csrf import is_csrf_token_valid
from data import notices

def redirect_to_notices():
    return redirect(url_for("browse_notices"))

def render_notices_template(notice_list):
    if notice_list is False:
        notice_list = []
        flash("Uutisten haku epäonnistui", "error")

    return render_template("browse_notices.html", notices=notice_list)

def render_notice_template(notice_id):
    return redirect(url_for("view_notice_details", notice_id=notice_id))

@app.route("/browse_notices")
@login_required
def browse_notices():
    notice_list = notices.get_all()
    return render_notices_template(notice_list)

@app.route("/browse_notices/my")
@login_required
def browse_my_notices():
    notice_list = notices.get_created_by_user()
    return render_notices_template(notice_list)

@app.route("/browse_notices/archived")
@admin_required
def browse_archived_notices():
    notice_list = notices.get_archived()
    return render_notices_template(notice_list)

@app.route("/browse_notices/nearby")
@login_required
def browse_nearby_notices():
    notice_list = notices.get_nearby()
    return render_notices_template(notice_list)

@app.route("/browse_notices/details/<int:notice_id>", methods=["GET", "POST"])
@login_required
def view_notice_details(notice_id):
    if request.method == "POST" and is_csrf_token_valid():
        notices.add_view(notice_id)

    notice = notices.get_details(notice_id)
    statuses = notices.get_statuses(notice_id)

    if notice:
        return render_template("notice_details.html", notice=notice, statuses=statuses)

    flash("Tietojen haku epäonnistui", "error")
    return redirect_to_notices()

@app.route("/support_notice/<int:notice_id>", methods=["POST"])
@login_required
def support_notice(notice_id):
    if not (is_csrf_token_valid() and notices.add_support(notice_id)):
        flash("Komppaaminen epäonnistui", "error")

    notice = notices.get_details(notice_id)

    if notice:
        return redirect(url_for("view_notice_details", notice_id=notice_id))

    flash("Tietojen haku epäonnistui", "error")
    return redirect_to_notices()

@app.route("/add_notice", methods=["GET", "POST"])
@login_required
def add_notice():
    if request.method == "GET":
        return render_template("add_notice.html")

    is_form_valid = is_csrf_token_valid()
    title = request.form["title"]
    body = request.form["body"]
    zip_code = request.form["zip_code"]
    street_address = request.form["street_address"]

    if len(title) < 1:
        flash("Otsikko ei saa olla tyhjä", "error")
        is_form_valid = False
    elif len(title) > 100:
        flash("Otsikossa voi olla enintään 100 merkkiä", "error")
        is_form_valid = False
    elif len(body) > 1000:
        flash("Lisätiedoissa voi olla enintään 1000 merkkiä", "error")
        is_form_valid = False

    if body == "":
        body = None

    if zip_code == "":
        zip_code = None
    elif len(zip_code) != 5:
        flash("Postinumerossa tulee olla 5 numeroa", "error")
        is_form_valid = False

    if street_address == "":
        street_address = None

    if is_form_valid and notices.add(title, body, zip_code, street_address):
        flash("Ilmoituksen tallennus onnistui", "error")
        return redirect_to_notices()

    flash("Ilmoituksen tallennus ei onnistunut", "error")
    return render_template("add_notice.html",
                            title=title,
                            body=body,
                            zip_code=zip_code,
                            street_address=street_address)

@app.route("/notice/acknowledge/<int:notice_id>", methods=["POST"])
@admin_required
def set_notice_as_acknowledged(notice_id):
    if not (is_csrf_token_valid() and notices.acknowledge(notice_id)):
        flash("Tilan päivitys ei onnistunut", "error")

    return render_notice_template(notice_id)

@app.route("/notice/wip/<int:notice_id>", methods=["POST"])
@admin_required
def set_notice_as_wip(notice_id):
    if not (is_csrf_token_valid() and notices.wip(notice_id)):
        flash("Tilan päivitys ei onnistunut", "error")

    return render_notice_template(notice_id)

@app.route("/notice/done/<int:notice_id>", methods=["POST"])
@admin_required
def set_notice_as_done(notice_id):
    if not (is_csrf_token_valid() and notices.done(notice_id)):
        flash("Tilan päivitys ei onnistunut", "error")

    return render_notice_template(notice_id)

@app.route("/notice/<int:notice_id>/delete_status/<int:status_id>", methods=["POST"])
@admin_required
def delete_status(notice_id, status_id):
    if not (is_csrf_token_valid() and notices.delete_status(status_id)):
        flash("Merkinnän poistaminen ei onnistunut", "error")

    return render_notice_template(notice_id)

@app.route("/archive_notice/<int:notice_id>", methods=["POST"])
@admin_required
def archive_notice(notice_id):
    if not (is_csrf_token_valid() and notices.archive(notice_id)):
        flash("Arkistointi ei onnistunut", "error")

    return redirect_to_notices()

@app.route("/unarchive_notice/<int:notice_id>", methods=["POST"])
@admin_required
def unarchive_notice(notice_id):
    if not (is_csrf_token_valid() and notices.unarchive(notice_id)):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect_to_notices()
