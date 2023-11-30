from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import flash, render_template, redirect, url_for, request, session
from werkzeug.security import check_password_hash
from app import app
from helpers.decorators import login_required
from helpers.csrf import is_csrf_token_valid
from data import users

@app.route("/profile")
@login_required
def profile():
    current_date = datetime.today().date()
    max_date = current_date - relativedelta(years=18)
    return render_template("profile.html", max_date=max_date)

@app.route("/update_date_of_birth", methods=["POST"])
@login_required
def update_date_of_birth():
    date_of_birth = request.form["date_of_birth"]

    if date_of_birth == "":
        date_of_birth = None

    user_id = session["user_id"]
    valid_token = is_csrf_token_valid()
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
    valid_token = is_csrf_token_valid()
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
    valid_token = is_csrf_token_valid()
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

    is_admin = request.form["is_admin"] == "yes"

    user_id = session["user_id"]
    valid_token = is_csrf_token_valid()
    data_updated = users.update_admin_status(user_id, is_admin)

    if not (user_id and valid_token and data_updated):
        flash("Tallennus ei onnistunut", "error")

    return redirect(url_for("profile"))

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "GET":
        return render_template("change_password.html")

    if "user_id" in session and "password_hash" in session:
        user_id = session["user_id"]
        password_hash = session["password_hash"]

        current_password = request.form["current_password"]
        password_match = check_password_hash(password_hash, current_password)
        new_password = request.form["new_password"]

        if not password_match:
            flash("Nykyinen salasana ei täsmää", "error")
        elif is_csrf_token_valid() and users.change_password(user_id, new_password):
            flash("Salasanan vaihtaminen onnistui")
            return redirect(url_for("profile"))

    flash("Salasanan vaihtaminen ei onnistunut", "error")
    return render_template("change_password.html",
                            current_password=current_password,
                            new_password=new_password)

@app.route("/delete_current_user", methods=["POST"])
@login_required
def delete_current_user():
    if "user_id" in session:
        user_id = session["user_id"]

        if is_csrf_token_valid() and users.delete_user(user_id):
            users.logout()
            return redirect("/")

    flash("Tilin poistaminen ei onnistunut", "error")
    return render_template("profile.html")
