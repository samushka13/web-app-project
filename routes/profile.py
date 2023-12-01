from flask import flash, render_template, redirect, url_for, request, session
from werkzeug.security import check_password_hash
from app import app
from helpers.decorators import login_required
from helpers.forms import (
    csrf_check_passed,
    get_date_of_birth,
    get_gender,
    get_zip_code,
    get_admin_status,
    get_max_date_of_birth
)
from helpers.validators import password_too_short, invalid_optional_date, invalid_zip_code
from data import users

def redirect_to_profile():
    return redirect(url_for("profile"))

@app.route("/profile")
@login_required
def profile():
    max_date = get_max_date_of_birth()
    return render_template("profile.html", max_date=max_date)

@app.route("/update_date_of_birth", methods=["POST"])
@login_required
def update_date_of_birth():
    date_of_birth = get_date_of_birth()

    if invalid_optional_date(date_of_birth):
        flash("Päivämäärä ei ole kelvollinen", "error")

    if not (csrf_check_passed() and users.update_date_of_birth(date_of_birth)):
        flash("Tallennus ei onnistunut", "error")

    return redirect_to_profile()

@app.route("/update_gender", methods=["POST"])
@login_required
def update_gender():
    gender = get_gender()

    if not (csrf_check_passed() and users.update_gender(gender)):
        flash("Tallennus ei onnistunut", "error")

    return redirect_to_profile()

@app.route("/update_zip_code", methods=["POST"])
@login_required
def update_zip_code():
    zip_code = get_zip_code()

    if invalid_zip_code(zip_code):
        flash("Postinumerossa tulee olla 5 numeroa", "error")
        return redirect_to_profile()

    if not (csrf_check_passed() and users.update_zip_code(zip_code)):
        flash("Tallennus ei onnistunut", "error")

    return redirect_to_profile()

@app.route("/update_admin_status", methods=["POST"])
@login_required
def update_admin_status():
    admin = get_admin_status()

    if not (csrf_check_passed() and users.update_admin_status(admin)):
        flash("Tallennus ei onnistunut", "error")

    return redirect_to_profile()

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "GET":
        return render_template("change_password.html")

    if "password_hash" in session:
        current_password = request.form["current_password"]
        password_match = check_password_hash(session["password_hash"], current_password)
        new_password = request.form["new_password"]

        if not password_match:
            flash("Nykyinen salasana ei täsmää", "error")
        elif password_too_short(new_password):
            flash("Uudessa salasanassa tulee olla vähintään 6 merkkiä", "error")
        elif csrf_check_passed() and users.change_password(new_password):
            flash("Salasanan vaihtaminen onnistui")
            return redirect_to_profile()

    flash("Salasanan vaihtaminen ei onnistunut", "error")
    return render_template("change_password.html",
                            current_password=current_password,
                            new_password=new_password)

@app.route("/delete_current_user", methods=["POST"])
@login_required
def delete_current_user():
    if csrf_check_passed() and users.delete_current_user():
        users.logout()
        return redirect("/")

    flash("Tilin poistaminen ei onnistunut", "error")
    return render_template("profile.html")
