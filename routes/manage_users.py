from flask import flash, render_template, redirect, url_for
from app import app
from helpers.decorators import admin_required
from helpers.csrf import is_csrf_token_valid
from data import users

@app.route("/manage_users")
@admin_required
def manage_users():
    user_list = users.get_users()
    return render_template("manage_users.html", users=user_list)

@app.route("/disable_user/<int:user_id>", methods=["POST"])
@admin_required
def disable_user(user_id):
    if not (is_csrf_token_valid() and users.disable_user(user_id)):
        flash("Tilin poistaminen käytöstä ei onnistunut", "error")

    return redirect(url_for("manage_users"))

@app.route("/enable_user/<int:user_id>", methods=["POST"])
@admin_required
def enable_user(user_id):
    if not (is_csrf_token_valid() and users.enable_user(user_id)):
        flash("Tilin ottaminen käyttöön ei onnistunut", "error")

    return redirect(url_for("manage_users"))
