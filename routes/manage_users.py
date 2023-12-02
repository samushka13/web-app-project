from flask import render_template, redirect, url_for, request
from app import app
from helpers import flashes
from helpers.decorators import admin_required
from helpers.forms import csrf_check_passed
from helpers.validators import username_too_long
from data import users

def redirect_to_users():
    return redirect(url_for("manage_users"))

@app.route("/manage_users")
@admin_required
def manage_users():
    if "username" not in request.args:
        user_list = users.get_users()
        return render_template("manage_users.html", users=user_list)

    user_input = request.args["username"]

    if username_too_long(user_input):
        user_list = []
        flashes.user_search_input_too_long()
    else:
        user_list = users.find_users(user_input)

    no_hits = len(user_list) == 0

    return render_template("manage_users.html",
                           users=user_list,
                           no_hits=no_hits,
                           user_input=user_input)

@app.route("/disable_user/<int:user_id>", methods=["POST"])
@admin_required
def disable_user(user_id):
    if not (csrf_check_passed() and users.disable_user(user_id)):
        flashes.account_disable_error()

    return redirect_to_users()

@app.route("/enable_user/<int:user_id>", methods=["POST"])
@admin_required
def enable_user(user_id):
    if not (csrf_check_passed() and users.enable_user(user_id)):
        flashes.account_enable_error()

    return redirect_to_users()
