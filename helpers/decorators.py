from functools import wraps
from flask import session, redirect, url_for

def login_required(fn):
    @wraps(fn)
    def logged_in(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("index"))
        return fn(*args, **kwargs)

    return logged_in

def admin_required(fn):
    @wraps(fn)
    def admin(*args, **kwargs):
        if "admin" not in session or not session["admin"]:
            return redirect(url_for("index"))
        return fn(*args, **kwargs)

    return admin
