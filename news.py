from sqlalchemy.sql import text
from db import db

def add(user_id: int, title: str, body: str, zip_code: str, publish_on: str):
    try:
        sql = """INSERT INTO news (title, body, zip_code, publish_on, created_at, created_by)
                 VALUES (:title, :body, :zip_code, :publish_on, NOW(), :created_by)"""

        values = {
            "title": title,
            "body": body,
            "zip_code": zip_code,
            "publish_on": publish_on,
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
                    N.id, N.title, N.body, N.zip_code, N.publish_on, N.created_at,
                    U.id as "user_id", U.name as "created_by"
                 FROM news AS N
                 JOIN users AS U
                 ON U.id=N.created_by
                 WHERE N.archived_at IS NULL"""

        result = db.session.execute(text(sql))
        news = result.fetchall()

        return news

    except Exception:
        return []

def get_archived():
    try:
        sql = """SELECT
                    N.id, N.title, N.body, N.zip_code, N.publish_on, N.created_at, N.archived_at,
                    U.id as "user_id", U.name as "created_by", U.name as "archived_by"
                 FROM news AS N
                 JOIN users AS U
                 ON U.id=N.created_by OR U.id=N.archived_by
                 WHERE N.archived_at IS NOT NULL"""

        result = db.session.execute(text(sql))
        news = result.fetchall()

        return news

    except Exception:
        return []

def get_upcoming():
    try:
        sql = """SELECT
                    N.id, N.title, N.body, N.zip_code, N.publish_on, N.created_at,
                    U.id as "user_id", U.name as "created_by", N.publish_on > CURRENT_DATE
                 FROM news AS N
                 JOIN users AS U
                 ON U.id=N.created_by
                 WHERE N.publish_on > CURRENT_DATE AND N.archived_at IS NULL"""

        result = db.session.execute(text(sql))
        news = result.fetchall()

        return news

    except Exception:
        return []
