from functools import wraps
from flask import session, redirect, url_for

def login_required(fn):
    @wraps(fn)
    def is_a_user_logged_in(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("index"))
        return fn(*args, **kwargs)

    return is_a_user_logged_in
