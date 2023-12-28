from flask import session
from sqlalchemy.sql import text
from helpers.contants import ITEMS_PER_PAGE
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

def get_current_count():
    sql = """SELECT COUNT(id)
            FROM news
            WHERE
                publish_on <= CURRENT_DATE
                AND archived_at IS NULL"""

    result = db.session.execute(text(sql))
    db.session.commit()

    return result.fetchone()[0]

def get_upcoming_count():
    sql = """SELECT COUNT(id)
            FROM news
            WHERE
                publish_on > CURRENT_DATE
                AND archived_at IS NULL"""

    result = db.session.execute(text(sql))
    db.session.commit()

    return result.fetchone()[0]

def get_archived_count():
    sql = """SELECT COUNT(id)
            FROM news
            WHERE archived_at IS NOT NULL"""

    result = db.session.execute(text(sql))
    db.session.commit()

    return result.fetchone()[0]

def get_nearby_count():
    zip_code = session["zip_code"]

    sql = """SELECT COUNT(id)
            FROM news
            WHERE
                publish_on <= CURRENT_DATE
                AND archived_at IS NULL
                AND zip_code=:zip_code"""

    values = {
        "zip_code": zip_code
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()[0]

def get_current(idx: int):
    sql = """SELECT
                id,
                title,
                body,
                zip_code,
                publish_on
            FROM news
            WHERE
                publish_on <= CURRENT_DATE
                AND archived_at IS NULL
            ORDER BY publish_on DESC
            LIMIT (:limit)
            OFFSET (:offset)"""

    values = {
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def get_upcoming(idx: int):
    sql = """SELECT
                id,
                title,
                body,
                zip_code,
                publish_on
            FROM news
            WHERE
                publish_on > CURRENT_DATE
                AND archived_at IS NULL
            ORDER BY publish_on ASC
            LIMIT (:limit)
            OFFSET (:offset)"""

    values = {
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def get_archived(idx: int):
    sql = """SELECT
                id,
                title,
                body,
                zip_code,
                publish_on,
                created_at,
                archived_at
            FROM news
            WHERE archived_at IS NOT NULL
            ORDER BY publish_on DESC
            LIMIT (:limit)
            OFFSET (:offset)"""

    values = {
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def get_nearby(idx: int):
    zip_code = session["zip_code"]

    sql = """SELECT
                id,
                title,
                body,
                zip_code,
                publish_on,
                created_at
            FROM news
            WHERE
                publish_on <= CURRENT_DATE
                AND archived_at IS NULL
                AND zip_code=:zip_code
            ORDER BY publish_on DESC
            LIMIT (:limit)
            OFFSET (:offset)"""

    values = {
        "zip_code": zip_code,
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
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
