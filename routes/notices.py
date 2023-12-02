from flask import render_template, redirect, url_for, request
from app import app
from helpers import flashes
from helpers.decorators import login_required, admin_required
from helpers.forms import (
    csrf_check_passed,
    get_body,
    get_zip_code,
    get_street_address,
    get_referrer
)
from helpers.pagination import get_pagination_variables
from helpers.validators import (
    no_title,
    title_too_long,
    body_too_long,
    invalid_zip_code,
    invalid_street_address
)
from data import notices

def redirect_to_notices():
    if "referrer" in request.form:
        if "nearby" in request.form["referrer"]:
            return redirect(url_for("browse_nearby_notices"))
        if "my" in request.form["referrer"]:
            return redirect(url_for("browse_my_notices"))
        if "archived" in request.form["referrer"]:
            return redirect(url_for("browse_archived_notices"))

    return redirect(url_for("browse_notices"))

def render_notices_template(idx, last_idx, count, count_on_next_idx, notice_list):
    return render_template("browse_notices.html",
                           idx=idx,
                           last_idx=last_idx,
                           count=count,
                           count_on_next_idx=count_on_next_idx,
                           notices=notice_list)

def render_notice_template(notice_id):
    return redirect(url_for("view_notice_details", notice_id=notice_id))

@app.route("/browse_notices")
@login_required
def browse_notices():
    pagination_vars = get_pagination_variables(notices.get_all_count())
    notice_list = notices.get_all(pagination_vars[0])
    return render_notices_template(*pagination_vars, notice_list)

@app.route("/browse_notices/my")
@login_required
def browse_my_notices():
    pagination_vars = get_pagination_variables(notices.get_created_by_user_count())
    notice_list = notices.get_created_by_user(pagination_vars[0])
    return render_notices_template(*pagination_vars, notice_list)

@app.route("/browse_notices/archived")
@admin_required
def browse_archived_notices():
    pagination_vars = get_pagination_variables(notices.get_archived_count())
    notice_list = notices.get_archived(pagination_vars[0])
    return render_notices_template(*pagination_vars, notice_list)

@app.route("/browse_notices/nearby")
@login_required
def browse_nearby_notices():
    pagination_vars = get_pagination_variables(notices.get_nearby_count())
    notice_list = notices.get_nearby(pagination_vars[0])
    return render_notices_template(*pagination_vars, notice_list)

@app.route("/browse_notices/details/<int:notice_id>", methods=["GET", "POST"])
@login_required
def view_notice_details(notice_id):
    if request.method == "POST" and csrf_check_passed():
        notices.add_view(notice_id)

    notice = notices.get_details(notice_id)
    statuses = notices.get_statuses(notice_id)
    referrer = get_referrer()

    if notice:
        return render_template("notice_details.html",
                               notice=notice,
                               statuses=statuses,
                               referrer=referrer)

    flashes.data_fetch_failed()
    return redirect_to_notices()

@app.route("/support_notice/<int:notice_id>", methods=["POST"])
@login_required
def support_notice(notice_id):
    if not (csrf_check_passed() and notices.add_support(notice_id)):
        flashes.support_error()

    return redirect(url_for("view_notice_details", notice_id=notice_id))

@app.route("/add_notice", methods=["GET", "POST"])
@login_required
def add_notice():
    if request.method == "GET":
        return render_template("add_notice.html")

    form_valid = csrf_check_passed()
    title = request.form["title"]
    body = get_body()
    zip_code = get_zip_code()
    street_address = get_street_address()

    if no_title(title):
        flashes.no_title()
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
    if not (csrf_check_passed() and notices.acknowledge(notice_id)):
        flashes.notice_status_update_error()

    return render_notice_template(notice_id)

@app.route("/notice/wip/<int:notice_id>", methods=["POST"])
@admin_required
def set_notice_as_wip(notice_id):
    if not (csrf_check_passed() and notices.wip(notice_id)):
        flashes.notice_status_update_error()

    return render_notice_template(notice_id)

@app.route("/notice/done/<int:notice_id>", methods=["POST"])
@admin_required
def set_notice_as_done(notice_id):
    if not (csrf_check_passed() and notices.done(notice_id)):
        flashes.notice_status_update_error()

    return render_notice_template(notice_id)

@app.route("/notice/<int:notice_id>/delete_status/<int:status_id>", methods=["POST"])
@admin_required
def delete_status(notice_id, status_id):
    if not (csrf_check_passed() and notices.delete_status(status_id)):
        flashes.notice_status_delete_error()

    return render_notice_template(notice_id)

@app.route("/archive_notice/<int:notice_id>", methods=["POST"])
@admin_required
def archive_notice(notice_id):
    if csrf_check_passed() and notices.archive(notice_id):
        flashes.archived()
    else:
        flashes.archiving_error()

    return redirect_to_notices()

@app.route("/unarchive_notice/<int:notice_id>", methods=["POST"])
@admin_required
def unarchive_notice(notice_id):
    if csrf_check_passed() and notices.unarchive(notice_id):
        flashes.unarchived()
    else:
        flashes.unarchiving_error()

    return redirect_to_notices()
