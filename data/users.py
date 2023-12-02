import os
from flask import session
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers.contants import ITEMS_PER_PAGE
from db import db

def register(name: str, password: str, date_of_birth: str, gender: str, zip_code: str, admin: bool):
    hash_value = generate_password_hash(password)

    try:
        sql = """INSERT INTO users
                    (name, password, date_of_birth, gender, zip_code, admin)
                 VALUES
                    (:name, :password, :date_of_birth, :gender, :zip_code, :admin)
                RETURNING id"""

        values = {
            "name": name,
            "password": hash_value,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "zip_code": zip_code,
            "admin": admin
        }

        result = db.session.execute(text(sql), values)
        db.session.commit()

        return result.fetchone()

    except IntegrityError:
        return None

def login(name: str, password: str):
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

    if not (user and check_password_hash(user[1], password)):
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
    session["admin"] = user[5]

    csrf_token = os.urandom(16).hex()
    session["csrf_token"] = csrf_token

    return "success"

def logout():
    for key in list(session.keys()):
        session.pop(key)

def update_date_of_birth(date_of_birth: str):
    sql = """UPDATE users
            SET date_of_birth=:date_of_birth
            WHERE id=:id
            RETURNING id"""

    values = {
        "date_of_birth": date_of_birth,
        "id": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    item = result.fetchone()

    if item:
        session["date_of_birth"] = date_of_birth

    return item

def update_gender(gender: str):
    sql = """UPDATE users
            SET gender=:gender
            WHERE id=:id
            RETURNING id"""

    values = {
        "gender": gender,
        "id": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    item = result.fetchone()

    if item:
        session["gender"] = gender

    return item

def update_zip_code(zip_code: str):
    sql = """UPDATE users
            SET zip_code=:zip_code
            WHERE id=:id
            RETURNING id"""

    values = {
        "zip_code": zip_code,
        "id": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    item = result.fetchone()

    if item:
        session["zip_code"] = zip_code

    return item

def update_admin_status(admin: bool):
    sql = """UPDATE users
            SET admin=:admin
            WHERE id=:id
            RETURNING id"""

    values = {
        "admin": admin,
        "id": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    item = result.fetchone()

    if item:
        session["admin"] = admin

    return item

def change_password(password: str):
    hash_value = generate_password_hash(password)

    sql = """UPDATE users
            SET password=:password
            WHERE id=:id
            RETURNING id"""

    values = {
        "password": hash_value,
        "id": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    item = result.fetchone()

    if item:
        session["password_hash"] = hash_value

    return item

def delete_current_user():
    sql = """DELETE FROM users
            WHERE id=:id
            RETURNING id"""

    values = {
        "id": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def get_user_count():
    sql = """SELECT COUNT(id)
            FROM users"""

    result = db.session.execute(text(sql))

    return result.fetchone()[0]

def get_find_user_count(user_input: str):
    sql = """SELECT COUNT(id)
            FROM users
            WHERE name LIKE :user_input"""

    values = {
        "user_input": f'%{user_input}%'
    }

    result = db.session.execute(text(sql), values)

    return result.fetchone()[0]

def get_users(idx: int):
    sql = """SELECT
                id,
                name,
                admin,
                disabled_at
            FROM users
            ORDER BY name ASC
            LIMIT (:limit)
            OFFSET (:offset)"""

    values = {
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def find_users(idx: int, user_input: str):
    sql = """SELECT
                id,
                name,
                admin,
                disabled_at
            FROM users
            WHERE name LIKE :user_input
            ORDER BY name ASC
            LIMIT (:limit)
            OFFSET (:offset)"""

    values = {
        "user_input": f'%{user_input}%',
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def disable_user(user_id: int):
    sql = """UPDATE users
            SET
                disabled_at=NOW(),
                disabled_by=:disabled_by
            WHERE id=:id
            RETURNING id"""

    values = {
        "disabled_by": session["user_id"],
        "id": user_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def enable_user(user_id: int):
    sql = """UPDATE users
            SET
                disabled_at=NULL,
                disabled_by=NULL
            WHERE id=:id
            RETURNING id"""

    values = {
        "id": user_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()
