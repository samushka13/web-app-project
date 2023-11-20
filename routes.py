from app import app
from flask import render_template

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/news")
def news():
    return render_template("news.html")

@app.route("/notices")
def notices():
    return render_template("notices.html")

@app.route("/polls")
def polls():
    return render_template("polls.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/add_news")
def add_news():
    return render_template("add_news.html")

@app.route("/add_notice")
def add_notice():
    return render_template("add_notice.html")

@app.route("/add_poll")
def add_poll():
    return render_template("add_poll.html")
