from flask import session
from sqlalchemy.sql import text
from db import db

def add(title: str, body: str, zip_code: str, publish_on: str):
    sql = """INSERT INTO news
                (title, body, zip_code, publish_on, created_at, created_by)
            VALUES
                (:title, :body, :zip_code, :publish_on, NOW(), :created_by)
            RETURNING id"""

    values = {
        "title": title,
        "body": body,
        "zip_code": zip_code,
        "publish_on": publish_on,
        "created_by": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def get_current():
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

    return result.fetchall()

def get_upcoming():
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

    return result.fetchall()

def get_archived():
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

    return result.fetchall()

def get_nearby():
    zip_code = session["zip_code"]

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
                AND N.zip_code=:zip_code
            ORDER BY N.publish_on DESC"""

    values = {
        "zip_code": zip_code
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def get_details(news_id: int):
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

    return result.fetchone()

def archive(news_id: int):
    sql = """UPDATE news
            SET
                archived_at=NOW(),
                archived_by=:archived_by
            WHERE id=:id
            RETURNING id"""

    values = {
        "archived_by": session["user_id"],
        "id": news_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def unarchive(news_id: int):
    sql = """UPDATE news
            SET
                archived_at=NULL,
                archived_by=NULL
            WHERE id=:id
            RETURNING id"""

    values = {
        "id": news_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def add_view(news_id: int):
    sql = """INSERT INTO news_views
                (news_id, viewed_at, viewed_by)
            VALUES
                (:news_id, NOW(), :viewed_by)
            RETURNING id"""

    values = {
        "news_id": news_id,
        "viewed_by": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()
