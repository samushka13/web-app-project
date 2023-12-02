from flask import render_template, redirect, url_for, request
from app import app
from helpers import flashes
from helpers.decorators import admin_required
from helpers.forms import csrf_check_passed
from helpers.pagination import get_pagination_variables
from helpers.validators import username_too_long
from data import users

def redirect_to_users():
    return redirect(url_for("manage_users"))

def render_users_template(idx, last_idx, count, count_on_next_idx, user_list, no_hits, user_input):
    return render_template("manage_users.html",
                           idx=idx,
                           last_idx=last_idx,
                           count=count,
                           count_on_next_idx=count_on_next_idx,
                           users=user_list,
                           no_hits=no_hits,
                           user_input=user_input)

@app.route("/manage_users", methods=["GET", "POST"])
@admin_required
def manage_users():
    if "username" not in request.form:
        pagination_vars = get_pagination_variables(users.get_user_count())
        user_list = users.get_users(pagination_vars[0])
        return render_users_template(*pagination_vars, user_list, False, "")

    user_input = request.form["username"]

    if username_too_long(user_input):
        pagination_vars = [0, 0, 0, 0]
        user_list = []
        flashes.user_search_input_too_long()
    else:
        pagination_vars = get_pagination_variables(users.get_find_user_count(user_input))
        user_list = users.find_users(pagination_vars[0], user_input)

    no_hits = len(user_list) == 0

    return render_users_template(*pagination_vars, user_list, no_hits, user_input)

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
