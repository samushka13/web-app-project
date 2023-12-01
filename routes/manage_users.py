from flask import render_template, redirect, url_for
from app import app
from helpers import flashes
from helpers.decorators import admin_required
from helpers.forms import csrf_check_passed
from data import users

@app.route("/manage_users")
@admin_required
def manage_users():
    user_list = users.get_users()
    return render_template("manage_users.html", users=user_list)

@app.route("/disable_user/<int:user_id>", methods=["POST"])
@admin_required
def disable_user(user_id):
    if not (csrf_check_passed() and users.disable_user(user_id)):
        flashes.account_disable_error()

    return redirect(url_for("manage_users"))

@app.route("/enable_user/<int:user_id>", methods=["POST"])
@admin_required
def enable_user(user_id):
    if not (csrf_check_passed() and users.enable_user(user_id)):
        flashes.account_enable_error()

    return redirect(url_for("manage_users"))
