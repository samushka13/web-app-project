from flask import flash, render_template, redirect, url_for, request, session
from app import app
from helpers.decorators import login_required, admin_required
from helpers.csrf import is_csrf_token_valid
from data import notices

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

@app.route("/browse_notices/nearby")
@login_required
def browse_nearby_notices():
    notice_list = notices.get_nearby(session["zip_code"])
    return render_template("browse_notices.html", notices=notice_list)

@app.route("/browse_notices/details/<int:notice_id>", methods=["GET", "POST"])
@login_required
def view_notice_details(notice_id):
    if request.method == "POST" and "user_id" in session and is_csrf_token_valid():
        notices.add_view(notice_id, session["user_id"])

    notice = notices.get_details(notice_id)

    if notice:
        return render_template("notice_details.html", notice=notice)

    flash("Tietojen haku epäonnistui", "error")
    return redirect(url_for("browse_notices"))

@app.route("/support_notice/<int:notice_id>", methods=["POST"])
@login_required
def support_notice(notice_id):
    if "user_id" in session and is_csrf_token_valid():
        supported = notices.add_support(notice_id, session["user_id"])
        if not supported:
            flash("Komppaaminen epäonnistui", "error")

    notice = notices.get_details(notice_id)

    if notice:
        return redirect(url_for("view_notice_details", notice_id=notice_id))

    flash("Tietojen haku epäonnistui", "error")
    return redirect(url_for("browse_notices"))

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
            data_updated = notices.add(user_id, title, body, zip_code, street_address)

            if not (user_id and is_csrf_token_valid() and data_updated):
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
    data_updated = notices.archive(user_id, notice_id)

    if not (user_id and is_csrf_token_valid() and data_updated):
        flash("Arkistointi ei onnistunut", "error")

    return redirect(url_for("browse_notices"))

@app.route("/unarchive_notice/<int:notice_id>", methods=["POST"])
@admin_required
def unarchive_notice(notice_id):
    user_id = session["user_id"]
    data_updated = notices.unarchive(user_id, notice_id)

    if not (user_id and is_csrf_token_valid() and data_updated):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect(url_for("browse_notices"))
