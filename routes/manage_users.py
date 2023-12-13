from flask import render_template, redirect, url_for, request
from app import app
from helpers import flashes
from helpers.decorators import admin_required
from helpers.forms import csrf_check_ok
from helpers.pagination import get_pagination_data
from helpers.validators import username_too_long
from data import users

def redirect_to_users(search: str, idx: int):
    return redirect(url_for("manage_users", search=search, idx=idx))

def render_users_template(idx,
                          last_idx,
                          count,
                          count_on_next_idx,
                          page_numbers,
                          user_list,
                          no_hits,
                          search):
    return render_template("manage_users.html",
                           idx=idx,
                           last_idx=last_idx,
                           count=count,
                           count_on_next_idx=count_on_next_idx,
                           page_numbers=page_numbers,
                           users=user_list,
                           no_hits=no_hits,
                           search=search)

@app.route("/manage_users")
@admin_required
def manage_users():
    if "search" not in request.args:
        pagination_data = get_pagination_data(users.get_user_count())
        user_list = users.get_users(pagination_data[0])
        return render_users_template(*pagination_data, user_list, False, "")

    search = request.args["search"]

    if username_too_long(search):
        pagination_data = [0, 0, 0, 0]
        user_list = []
        flashes.search_input_too_long()
    else:
        pagination_data = get_pagination_data(users.get_search_user_count(search))
        user_list = users.search_users(pagination_data[0], search)

    no_hits = len(user_list) == 0

    return render_users_template(*pagination_data, user_list, no_hits, search)

@app.route("/disable_user/<int:user_id>", methods=["POST"])
@admin_required
def disable_user(user_id):
    if not (csrf_check_ok() and users.disable_user(user_id)):
        flashes.account_disable_error()

    search = request.form["search"]
    idx = request.form["idx"]

    return redirect_to_users(search, idx)

@app.route("/enable_user/<int:user_id>", methods=["POST"])
@admin_required
def enable_user(user_id):
    if not (csrf_check_ok() and users.enable_user(user_id)):
        flashes.account_enable_error()

    search = request.form["search"]
    idx = request.form["idx"]

    return redirect_to_users(search, idx)
