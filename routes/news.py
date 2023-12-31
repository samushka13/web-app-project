from datetime import datetime
from flask import render_template, redirect, url_for, request, session
from app import app
from helpers import flashes
from helpers.decorators import login_required, admin_required
from helpers.forms import csrf_check_ok, get_date, get_body, get_zip_code
from helpers.pagination import get_pagination_data
from helpers.validators import (
    title_too_short,
    title_too_long,
    body_too_long,
    invalid_zip_code,
    invalid_required_date
)
from data import news

def redirect_to_news():
    if "nearby" in session["referrer"]:
        return redirect(url_for("browse_nearby_news"))
    if "upcoming" in session["referrer"]:
        return redirect(url_for("browse_upcoming_news"))
    if "archived" in session["referrer"]:
        return redirect(url_for("browse_archived_news"))

    return redirect(url_for("browse_news"))

def render_news_template(idx, last_idx, count, count_on_next_idx, page_numbers, news_list):
    return render_template("browse_news.html",
                           idx=idx,
                           last_idx=last_idx,
                           count=count,
                           count_on_next_idx=count_on_next_idx,
                           page_numbers=page_numbers,
                           news=news_list)

@app.route("/browse_news")
@login_required
def browse_news():
    pagination_data = get_pagination_data(news.get_current_count())
    news_list = news.get_current(pagination_data[0])
    session["referrer"] = "/browse_news"
    return render_news_template(*pagination_data, news_list)

@app.route("/browse_news/upcoming")
@admin_required
def browse_upcoming_news():
    pagination_data = get_pagination_data(news.get_upcoming_count())
    news_list = news.get_upcoming(pagination_data[0])
    session["referrer"] = "/browse_news/upcoming"
    return render_news_template(*pagination_data, news_list)

@app.route("/browse_news/archived")
@admin_required
def browse_archived_news():
    pagination_data = get_pagination_data(news.get_archived_count())
    news_list = news.get_archived(pagination_data[0])
    session["referrer"] = "/browse_news/archived"
    return render_news_template(*pagination_data, news_list)

@app.route("/browse_news/nearby")
@login_required
def browse_nearby_news():
    pagination_data = get_pagination_data(news.get_nearby_count())
    news_list = news.get_nearby(pagination_data[0])
    session["referrer"] = "/browse_news/nearby"
    return render_news_template(*pagination_data, news_list)

@app.route("/browse_news/details/<int:news_id>", methods=["GET", "POST"])
@login_required
def view_news_details(news_id):
    if request.method == "POST" and csrf_check_ok():
        news.add_view(news_id)

    if "news" not in session["referrer"]:
        session["referrer"] = "/browse_news"

    item = news.get_details(news_id)

    if item:
        return render_template("news_details.html", item=item)

    flashes.data_fetch_failed()
    return redirect_to_news()

@app.route("/add_news", methods=["GET", "POST"])
@admin_required
def add_news():
    if "news" not in session["referrer"]:
        session["referrer"] = "/browse_news"

    if request.method == "GET":
        current_date = datetime.today().date()
        return render_template("add_news.html", current_date=current_date)

    form_valid = csrf_check_ok()
    title = request.form["title"]
    body = get_body()
    zip_code = get_zip_code()
    publish_on = get_date("publish_on")

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
    elif invalid_required_date(publish_on):
        flashes.invalid_date()
        form_valid = False

    if form_valid and news.add(title, body, zip_code, publish_on):
        flashes.news_saved()
        return redirect_to_news()

    flashes.news_save_error()
    return render_template("add_news.html",
                            title=title,
                            body=body,
                            zip_code=zip_code,
                            publish_on=publish_on)

@app.route("/archive_news/<int:news_id>", methods=["POST"])
@admin_required
def archive_news(news_id):
    if csrf_check_ok() and news.archive(news_id):
        flashes.archived()
    else:
        flashes.archiving_error()

    return redirect_to_news()

@app.route("/unarchive_news/<int:news_id>", methods=["POST"])
@admin_required
def unarchive_news(news_id):
    if csrf_check_ok() and news.unarchive(news_id):
        flashes.unarchived()
    else:
        flashes.unarchiving_error()

    return redirect_to_news()
