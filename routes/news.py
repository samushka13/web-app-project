from datetime import datetime
from flask import flash, render_template, redirect, url_for, request, session
from app import app
from helpers.decorators import login_required, admin_required
from helpers.csrf import is_csrf_token_valid
from data import news

def render_news_template(news_list):
    if news_list is False:
        news_list = []
        flash("Uutisten haku epäonnistui", "error")

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
    news_list = news.get_nearby(session["zip_code"])
    return render_news_template(news_list)

@app.route("/browse_news/details/<int:news_id>", methods=["GET", "POST"])
@login_required
def view_news_details(news_id):
    if request.method == "POST" and is_csrf_token_valid():
        news.add_view(news_id, session["user_id"])

    item = news.get_details(news_id)

    if item:
        return render_template("news_details.html", item=item)

    flash("Tietojen haku epäonnistui", "error")
    return redirect(url_for("browse_news"))

@app.route("/add_news", methods=["GET", "POST"])
@admin_required
def add_news():
    if request.method == "GET":
        current_date = datetime.today().date()
        return render_template("add_news.html", current_date=current_date)

    if request.method == "POST":
        is_form_valid = is_csrf_token_valid()
        title = request.form["title"]
        body = request.form["body"]
        zip_code = request.form["zip_code"]
        publish_on = request.form["publish_on"]

        if len(title) < 1:
            flash("Otsikko ei saa olla tyhjä", "error")
            is_form_valid = False
        elif len(title) > 100:
            flash("Otsikossa voi olla enintään 100 merkkiä", "error")
            is_form_valid = False
        elif len(body) > 1000:
            flash("Lisätiedoissa voi olla enintään 1000 merkkiä", "error")
            is_form_valid = False

        if body == "":
            body = None

        if zip_code == "":
            zip_code = None
        elif len(zip_code) != 5:
            flash("Postinumerossa tulee olla 5 numeroa", "error")
            is_form_valid = False

        if not publish_on or len(publish_on) < 10:
            flash("Päivämäärä ei ole kelvollinen")
            is_form_valid = False

        if is_form_valid and news.add(session["user_id"], title, body, zip_code, publish_on):
            flash("Uutisen tallennus onnistui")
            return redirect(url_for("browse_news"))

        flash("Uutisen tallennus ei onnistunut", "error")
        return render_template("add_news.html",
                                title=title,
                                body=body,
                                zip_code=zip_code,
                                publish_on=publish_on)

@app.route("/archive_news/<int:news_id>", methods=["POST"])
@admin_required
def archive_news(news_id):
    if not (is_csrf_token_valid() and news.archive(session["user_id"], news_id)):
        flash("Arkistointi ei onnistunut", "error")

    return redirect(url_for("browse_news"))

@app.route("/unarchive_news/<int:news_id>", methods=["POST"])
@admin_required
def unarchive_news(news_id):
    if not (is_csrf_token_valid() and news.unarchive(session["user_id"], news_id)):
        flash("Arkistoinnin peruminen ei onnistunut", "error")

    return redirect(url_for("browse_news"))
