from datetime import datetime
from flask import flash, render_template, redirect, url_for, request
from app import app
from helpers.decorators import login_required, admin_required
from helpers.forms import csrf_check_passed, get_date, get_body, get_zip_code
from helpers.validators import (
    no_title,
    title_too_long,
    body_too_long,
    invalid_zip_code,
    invalid_required_date
)
from data import news

def redirect_to_news():
    return redirect(url_for("browse_news"))

def render_news_template(news_list):
    return render_template("browse_news.html", news=news_list)

@app.route("/browse_news")
@login_required
def browse_news():
    news_list = news.get_current()
    return render_news_template(news_list)

@app.route("/browse_news/upcoming")
@admin_required
def browse_upcoming_news():
    news_list = news.get_upcoming()
    return render_news_template(news_list)

@app.route("/browse_news/archived")
@admin_required
def browse_archived_news():
    news_list = news.get_archived()
    return render_news_template(news_list)

@app.route("/browse_news/nearby")
@login_required
def browse_nearby_news():
    news_list = news.get_nearby()
    return render_news_template(news_list)

@app.route("/browse_news/details/<int:news_id>", methods=["GET", "POST"])
@login_required
def view_news_details(news_id):
    if request.method == "POST" and csrf_check_passed():
        news.add_view(news_id)

    item = news.get_details(news_id)

    if item:
        return render_template("news_details.html", item=item)

    flash("Tietojen haku epäonnistui", "error")
    return redirect_to_news()

@app.route("/add_news", methods=["GET", "POST"])
@admin_required
def add_news():
    if request.method == "GET":
        current_date = datetime.today().date()
        return render_template("add_news.html", current_date=current_date)

    form_valid = csrf_check_passed()
    title = request.form["title"]
    body = get_body()
    zip_code = get_zip_code()
    publish_on = get_date("publish_on")

    if no_title(title):
        flash("Otsikko ei saa olla tyhjä", "error")
        form_valid = False
    elif title_too_long(title):
        flash("Otsikossa voi olla enintään 100 merkkiä", "error")
        form_valid = False
    elif body_too_long(body):
        flash("Lisätiedoissa voi olla enintään 1000 merkkiä", "error")
        form_valid = False
    elif invalid_zip_code(zip_code):
        flash("Postinumerossa tulee olla 5 numeroa", "error")
        form_valid = False
    elif invalid_required_date(publish_on):
        flash("Päivämäärä ei ole kelvollinen", "error")
        form_valid = False

    if form_valid and news.add(title, body, zip_code, publish_on):
        flash("Uutisen tallennus onnistui")
        return redirect_to_news()

    flash("Uutisen tallennus ei onnistunut", "error")
    return render_template("add_news.html",
                            title=title,
                            body=body,
                            zip_code=zip_code,
                            publish_on=publish_on)

@app.route("/archive_news/<int:news_id>", methods=["POST"])
@admin_required
def archive_news(news_id):
    if not (csrf_check_passed() and news.archive(news_id)):
        flash("Arkistointi ei onnistunut", "error")

    return redirect_to_news()

@app.route("/unarchive_news/<int:news_id>", methods=["POST"])
@admin_required
def unarchive_news(news_id):
    if not (csrf_check_passed() and news.unarchive(news_id)):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect_to_news()
