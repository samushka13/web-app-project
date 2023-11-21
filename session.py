from flask import request, session

def is_csrf_token_valid():
    return session["csrf_token"] == request.form["csrf_token"]
