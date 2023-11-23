from sqlalchemy.sql import text
from db import db

def add(user_id: int, title: str, zip_code: str, open_on: str, close_on: str):
    try:
        sql = """INSERT INTO polls (title, zip_code, open_on, close_on, created_at, created_by)
                 VALUES (:title, :zip_code, :open_on, :close_on, NOW(), :created_by)"""

        values = {
            "title": title,
            "zip_code": zip_code,
            "open_on": open_on,
            "close_on": close_on,
            "created_by": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def get_all():
    sql = """SELECT
                P.id,
                P.title as title,
                P.zip_code as zip_code,
                to_char(DATE(P.open_on)::date, 'DD.MM.YYYY') as open_on,
                to_char(DATE(P.close_on)::date, 'DD.MM.YYYY') as close_on,
                U.id,
                U.name as "created_by"
             FROM polls AS P
             JOIN users AS U
             ON U.id=P.created_by"""

    result = db.session.execute(text(sql))
    polls = result.fetchall()

    return polls
