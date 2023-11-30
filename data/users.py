import os
from flask import session
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from db import db

def register(name: str, password: str, date_of_birth: str, gender: str, zip_code: str, admin: bool):
    hash_value = generate_password_hash(password)

    try:
        sql = """INSERT INTO users
                    (name, password, date_of_birth, gender, zip_code, admin)
                 VALUES
                    (:name, :password, :date_of_birth, :gender, :zip_code, :admin)"""

        values = {
            "name": name,
            "password": hash_value,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "zip_code": zip_code,
            "admin": admin
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except IntegrityError:
        return "username-exists"

    except Exception:
        return False

    login(name, password)

    return True

def login(name: str, password: str):
    try:
        sql = """SELECT
                    id,
                    password,
                    to_char(DATE(date_of_birth)::date, 'YYYY-MM-DD'),
                    gender,
                    zip_code,
                    admin,
                    disabled_at
                 FROM users
                 WHERE name=:name"""

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
        session["password_hash"] = user[1]
        session["date_of_birth"] = user[2]
        session["gender"] = user[3]
        session["zip_code"] = user[4]
        session["is_admin"] = user[5]

        csrf_token = os.urandom(16).hex()
        session["csrf_token"] = csrf_token

    except Exception:
        return False

    return True

def logout():
    for key in list(session.keys()):
        session.pop(key)

def update_date_of_birth(date_of_birth: str):
    try:
        user_id = session["user_id"]

        sql = """UPDATE users
                 SET date_of_birth=:date_of_birth
                 WHERE id=:id"""

        values = {
            "date_of_birth": date_of_birth,
            "id": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    session["date_of_birth"] = date_of_birth

    return True

def update_gender(gender: str):
    try:
        user_id = session["user_id"]

        sql = """UPDATE users
                 SET gender=:gender
                 WHERE id=:id"""

        values = {
            "gender": gender,
            "id": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    session["gender"] = gender

    return True

def update_zip_code(zip_code: str):
    try:
        user_id = session["user_id"]

        sql = """UPDATE users
                 SET zip_code=:zip_code
                 WHERE id=:id"""

        values = {
            "zip_code": zip_code,
            "id": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    session["zip_code"] = zip_code

    return True

def update_admin_status(is_admin: str):
    try:
        user_id = session["user_id"]

        sql = """UPDATE users
                 SET admin=:admin
                 WHERE id=:id"""

        values = {
            "admin": is_admin,
            "id": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    session["is_admin"] = is_admin

    return True

def change_password(password: str):
    hash_value = generate_password_hash(password)

    try:
        user_id = session["user_id"]

        sql = """UPDATE users
                 SET password=:password
                 WHERE id=:id"""

        values = {
            "password": hash_value,
            "id": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def delete_current_user():
    try:
        user_id = session["user_id"]

        sql = """DELETE FROM users
                 WHERE id=:id"""

        values = {
            "id": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def get_users():
    try:
        sql = """SELECT
                    id,
                    name,
                    admin,
                    disabled_at
                 FROM users
                 ORDER BY name ASC"""

        result = db.session.execute(text(sql))
        users = result.fetchall()

        return users

    except Exception:
        return []

def disable_user(user_id: int):
    try:
        sql = """UPDATE users
                 SET
                    disabled_at=NOW(),
                    disabled_by=:disabled_by
                 WHERE id=:id"""

        values = {
            "disabled_by": session["user_id"],
            "id": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def enable_user(user_id: int):
    try:
        sql = """UPDATE users
                 SET
                    disabled_at=NULL,
                    disabled_by=NULL
                 WHERE id=:id"""

        values = {
            "id": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True
