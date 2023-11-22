import os
from flask import request, session
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from db import db

def register(name: str, password: str, date_of_birth: str, gender: str, zip_code: str, admin: bool):
    hash_value = generate_password_hash(password)

    try:
        sql = """INSERT INTO users (name, password, date_of_birth, gender, zip_code, admin)
                 VALUES (:name, :password, :date_of_birth, :gender, :zip_code, :admin)"""

        new_user = {
            "name": name,
            "password": hash_value,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "zip_code": zip_code,
            "admin": admin
        }

        db.session.execute(text(sql), new_user)
        db.session.commit()

    except Exception:
        return False

    return True

def login(name: str, password: str):
    sql = """SELECT id, password, date_of_birth, gender, zip_code, admin, disabled
             FROM users WHERE name=:name"""

    result = db.session.execute(text(sql), { "name": name })
    user = result.fetchone()

    if not user:
        return "credential-error"

    password_match = check_password_hash(user[1], password)

    if not password_match:
        return "credential-error"

    disabled = user[6]

    if disabled:
        return "account-disabled"

    session["username"] = name
    session["user_id"] = user[0]
    session["date_of_birth"] = user[2]
    session["gender"] = user[3]
    session["zip_code"] = user[4]
    session["is_admin"] = user[5]

    csrf_token = os.urandom(16).hex()
    session["csrf_token"] = csrf_token

    return True

def logout():
    for key in list(session.keys()):
        session.pop(key)

def delete_user(user_id: int):
    try:
        sql = f"DELETE FROM users WHERE id='{user_id}'"

        db.session.execute(text(sql))
        db.session.commit()

    except Exception:
        return False

    return True

def get_users():
    sql = """SELECT id, name, admin, disabled FROM users"""

    result = db.session.execute(text(sql))
    users = result.fetchall()

    return users

def disable_user(user_id: int):
    try:
        sql = f"UPDATE users SET disabled={True} WHERE id=:id"

        db.session.execute(text(sql), { "id": user_id })
        db.session.commit()

    except Exception:
        return False

    return True

def is_csrf_token_valid():
    return session["csrf_token"] == request.form["csrf_token"]
