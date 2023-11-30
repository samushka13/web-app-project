from flask import session
from sqlalchemy.sql import text
from db import db

def add(title: str, body: str, zip_code: str, publish_on: str):
    try:
        user_id = session["user_id"]

        sql = """INSERT INTO news
                    (title, body, zip_code, publish_on, created_at, created_by)
                 VALUES
                    (:title, :body, :zip_code, :publish_on, NOW(), :created_by)"""

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

def get_current():
    try:
        sql = """SELECT
                    N.id,
                    N.title,
                    N.body,
                    N.zip_code,
                    N.publish_on
                 FROM news AS N
                 WHERE
                    N.publish_on <= CURRENT_DATE
                    AND N.archived_at IS NULL
                 ORDER BY N.publish_on DESC"""

        result = db.session.execute(text(sql))
        news = result.fetchall()

        return news

    except Exception:
        return False

def get_upcoming():
    try:
        sql = """SELECT
                    N.id,
                    N.title,
                    N.body,
                    N.zip_code,
                    N.publish_on
                 FROM news AS N
                 WHERE
                    N.publish_on > CURRENT_DATE
                    AND N.archived_at IS NULL
                 ORDER BY N.publish_on ASC"""

        result = db.session.execute(text(sql))
        news = result.fetchall()

        return news

    except Exception:
        return False

def get_archived():
    try:
        sql = """SELECT
                    N.id,
                    N.title,
                    N.body,
                    N.zip_code,
                    N.publish_on,
                    N.created_at,
                    N.archived_at
                 FROM news AS N
                 WHERE N.archived_at IS NOT NULL
                 ORDER BY N.publish_on DESC"""

        result = db.session.execute(text(sql))
        news = result.fetchall()

        return news

    except Exception:
        return False

def get_nearby(user_zip_code: str):
    try:
        sql = """SELECT
                    N.id,
                    N.title,
                    N.body,
                    N.zip_code,
                    N.publish_on,
                    N.created_at
                 FROM news AS N
                 WHERE
                    N.archived_at IS NULL
                    AND N.zip_code=:user_zip_code
                 ORDER BY N.publish_on DESC"""

        values = {
            "user_zip_code": user_zip_code
        }

        result = db.session.execute(text(sql), values)
        news = result.fetchall()

        return news

    except Exception:
        return False

def get_details(news_id: int):
    try:
        sql = """SELECT
                    N.id,
                    N.title,
                    N.body,
                    N.zip_code,
                    N.publish_on,
                    N.created_at,
                    N.archived_at,
                    U.id as "user_id",
                    U.name as "created_by",
                    (SELECT name FROM users WHERE id=N.archived_by) as "archived_by",
                    (SELECT COUNT(viewed_by) FROM news_views WHERE news_id=:news_id) as "total_views",
                    (SELECT COUNT(DISTINCT viewed_by) FROM news_views WHERE news_id=:news_id) as "unique_views"
                 FROM news AS N
                 JOIN users AS U
                 ON U.id=N.created_by
                 WHERE N.id=:news_id"""

        values = {
            "news_id": news_id
        }

        result = db.session.execute(text(sql), values)
        item = result.fetchone()

        return item

    except Exception:
        return False

def archive(news_id: int):
    try:
        user_id = session["user_id"]

        sql = """UPDATE news
                 SET
                    archived_at=NOW(),
                    archived_by=:archived_by
                 WHERE id=:id"""

        values = {
            "archived_by": user_id,
            "id": news_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def unarchive(news_id: int):
    try:
        sql = """UPDATE news
                 SET
                    archived_at=NULL,
                    archived_by=NULL
                 WHERE id=:id"""

        values = {
            "id": news_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def add_view(news_id: int):
    try:
        user_id = session["user_id"]

        sql = """INSERT INTO news_views
                    (news_id, viewed_at, viewed_by)
                 VALUES
                    (:news_id, NOW(), :viewed_by)"""

        values = {
            "news_id": news_id,
            "viewed_by": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True
