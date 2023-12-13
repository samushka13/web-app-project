from flask import render_template, redirect, url_for, request, session
from app import app
from helpers import flashes
from helpers.decorators import login_required, admin_required
from helpers.forms import csrf_check_ok, get_body, get_zip_code, get_street_address
from helpers.pagination import get_pagination_data
from helpers.validators import (
    title_too_short,
    title_too_long,
    body_too_long,
    invalid_zip_code,
    invalid_street_address
)
from data import notices

def redirect_to_notices():
    if "nearby" in session["referrer"]:
        return redirect(url_for("browse_nearby_notices"))
    if "my" in session["referrer"]:
        return redirect(url_for("browse_my_notices"))
    if "archived" in session["referrer"]:
        return redirect(url_for("browse_archived_notices"))

    return redirect(url_for("browse_notices"))

def render_notices_template(idx, last_idx, count, count_on_next_idx, page_numbers, notice_list):
    return render_template("browse_notices.html",
                           idx=idx,
                           last_idx=last_idx,
                           count=count,
                           count_on_next_idx=count_on_next_idx,
                           page_numbers=page_numbers,
                           notices=notice_list)

def render_notice_template(notice_id):
    return redirect(url_for("view_notice_details", notice_id=notice_id))

@app.route("/browse_notices")
@login_required
def browse_notices():
    pagination_data = get_pagination_data(notices.get_all_count())
    notice_list = notices.get_all(pagination_data[0])
    session["referrer"] = "/browse_notices"
    return render_notices_template(*pagination_data, notice_list)

@app.route("/browse_notices/my")
@login_required
def browse_my_notices():
    pagination_data = get_pagination_data(notices.get_created_by_user_count())
    notice_list = notices.get_created_by_user(pagination_data[0])
    session["referrer"] = "/browse_notices/my"
    return render_notices_template(*pagination_data, notice_list)

@app.route("/browse_notices/archived")
@admin_required
def browse_archived_notices():
    pagination_data = get_pagination_data(notices.get_archived_count())
    notice_list = notices.get_archived(pagination_data[0])
    session["referrer"] = "/browse_notices/archived"
    return render_notices_template(*pagination_data, notice_list)

@app.route("/browse_notices/nearby")
@login_required
def browse_nearby_notices():
    pagination_data = get_pagination_data(notices.get_nearby_count())
    notice_list = notices.get_nearby(pagination_data[0])
    session["referrer"] = "/browse_notices/nearby"
    return render_notices_template(*pagination_data, notice_list)

@app.route("/browse_notices/details/<int:notice_id>", methods=["GET", "POST"])
@login_required
def view_notice_details(notice_id):
    if "notice" not in session["referrer"]:
        session["referrer"] = "/browse_notices"

    if request.method == "POST" and csrf_check_ok():
        notices.add_view(notice_id)

    notice = notices.get_details(notice_id)
    statuses = notices.get_statuses(notice_id)

    if notice:
        return render_template("notice_details.html", notice=notice, statuses=statuses)

    flashes.data_fetch_failed()
    return redirect_to_notices()

@app.route("/support_notice/<int:notice_id>", methods=["POST"])
@login_required
def support_notice(notice_id):
    if not (csrf_check_ok() and notices.add_support(notice_id)):
        flashes.support_error()

    return redirect(url_for("view_notice_details", notice_id=notice_id))

@app.route("/add_notice", methods=["GET", "POST"])
@login_required
def add_notice():
    if "notice" not in session["referrer"]:
        session["referrer"] = "/browse_notices"

    if request.method == "GET":
        return render_template("add_notice.html")

    form_valid = csrf_check_ok()
    title = request.form["title"]
    body = get_body()
    zip_code = get_zip_code()
    street_address = get_street_address()

    if title_too_short(title):
        flashes.title_too_short()
        form_valid = False
    elif title_too_long(title):
        flashes.title_too_long()
        form_valid = False
    elif body_too_long(body):
        flashes.body_too_long()
        form_valid = False
    elif invalid_zip_code(zip_code):
        flashes.invalid_zip_code()
        form_valid = False
    elif invalid_street_address(street_address):
        flashes.invalid_date()
        form_valid = False

    if form_valid and notices.add(title, body, zip_code, street_address):
        flashes.notice_saved()
        return redirect_to_notices()

    flashes.notice_save_error()
    return render_template("add_notice.html",
                            title=title,
                            body=body,
                            zip_code=zip_code,
                            street_address=street_address)

@app.route("/notice/acknowledge/<int:notice_id>", methods=["POST"])
@admin_required
def set_notice_as_acknowledged(notice_id):
    if not (csrf_check_ok() and notices.acknowledge(notice_id)):
        flashes.notice_status_update_error()

    return render_notice_template(notice_id)

@app.route("/notice/wip/<int:notice_id>", methods=["POST"])
@admin_required
def set_notice_as_wip(notice_id):
    if not (csrf_check_ok() and notices.wip(notice_id)):
        flashes.notice_status_update_error()

    return render_notice_template(notice_id)

@app.route("/notice/done/<int:notice_id>", methods=["POST"])
@admin_required
def set_notice_as_done(notice_id):
    if not (csrf_check_ok() and notices.done(notice_id)):
        flashes.notice_status_update_error()

    return render_notice_template(notice_id)

@app.route("/notice/<int:notice_id>/delete_status/<int:status_id>", methods=["POST"])
@admin_required
def delete_status(notice_id, status_id):
    if not (csrf_check_ok() and notices.delete_status(status_id)):
        flashes.notice_status_delete_error()

    return render_notice_template(notice_id)

@app.route("/archive_notice/<int:notice_id>", methods=["POST"])
@admin_required
def archive_notice(notice_id):
    if csrf_check_ok() and notices.archive(notice_id):
        flashes.archived()
    else:
        flashes.archiving_error()

    return redirect_to_notices()

@app.route("/unarchive_notice/<int:notice_id>", methods=["POST"])
@admin_required
def unarchive_notice(notice_id):
    if csrf_check_ok() and notices.unarchive(notice_id):
        flashes.unarchived()
    else:
        flashes.unarchiving_error()

    return redirect_to_notices()
