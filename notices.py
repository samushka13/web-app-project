from sqlalchemy.sql import text
from db import db

def add(user_id: int, title: str, body: str, zip_code: str, street_address: str):
    try:
        sql = """INSERT INTO notices (title, body, zip_code, street_address, created_at, created_by)
                 VALUES (:title, :body, :zip_code, :street_address, NOW(), :created_by)"""

        values = {
            "title": title,
            "body": body,
            "zip_code": zip_code,
            "street_address": street_address,
            "created_by": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def get_all():
    try:
        sql = """SELECT
                    N.id, N.title, N.body, N.zip_code, N.street_address, N.created_at,
                    U.id as "user_id", U.name as "created_by"
                 FROM notices AS N
                 JOIN users AS U
                 ON U.id=N.created_by
                 ORDER BY N.created_at DESC"""

        result = db.session.execute(text(sql))
        notices = result.fetchall()

        return notices

    except Exception:
        return []

def get_user_notices(user_id: int):
    try:
        sql = """SELECT
                    N.id, N.title, N.body, N.zip_code, N.street_address, N.created_at,
                    U.id as "user_id", U.name as "created_by"
                 FROM notices AS N
                 JOIN users AS U
                 ON U.id=N.created_by
                 WHERE :user_id=N.created_by
                 ORDER BY N.created_at DESC"""

        values = {
            "user_id": user_id
        }

        result = db.session.execute(text(sql), values)
        notices = result.fetchall()

        return notices

    except Exception:
        return []
