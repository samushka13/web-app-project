from flask import flash, render_template, redirect, url_for
from app import app
from helpers.decorators import admin_required
from helpers.forms import csrf_check_passed
from data import users

@app.route("/manage_users")
@admin_required
def manage_users():
    user_list = users.get_users()

    if user_list is False:
        user_list = []
        flash("Käyttäjien haku epäonnistui", "error")

    return render_template("manage_users.html", users=user_list)

@app.route("/disable_user/<int:user_id>", methods=["POST"])
@admin_required
def disable_user(user_id):
    if not (csrf_check_passed() and users.disable_user(user_id)):
        flash("Tilin poistaminen käytöstä ei onnistunut", "error")

    return redirect(url_for("manage_users"))

@app.route("/enable_user/<int:user_id>", methods=["POST"])
@admin_required
def enable_user(user_id):
    if not (csrf_check_passed() and users.enable_user(user_id)):
        flash("Tilin ottaminen käyttöön ei onnistunut", "error")

    return redirect(url_for("manage_users"))
