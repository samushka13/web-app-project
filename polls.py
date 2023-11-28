from sqlalchemy.sql import text
from db import db

def add(user_id: int, title: str, zip_code: str, open_on: str, close_on: str):
    try:
        sql = """INSERT INTO polls
                    (title, zip_code, open_on, close_on, created_at, created_by)
                 VALUES
                    (:title, :zip_code, :open_on, :close_on, NOW(), :created_by)"""

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

def get_current():
    try:
        sql = """SELECT
                    P.id,
                    P.title as "title",
                    P.zip_code as "zip_code",
                    to_char(DATE(P.open_on)::date, 'DD.MM.YYYY') as "open_on",
                    to_char(DATE(P.close_on)::date, 'DD.MM.YYYY') as "close_on",
                    P.created_at,
                    U.id as "user_id",
                    U.name as "created_by",
                    P.open_on <= CURRENT_DATE,
                    P.close_on > CURRENT_DATE
                 FROM polls AS P
                 JOIN users AS U
                 ON U.id=P.created_by
                 WHERE
                    P.open_on <= CURRENT_DATE
                    AND P.close_on > CURRENT_DATE
                    AND P.archived_at IS NULL
                 ORDER BY P.created_at DESC"""

        result = db.session.execute(text(sql))
        polls = result.fetchall()

        return polls

    except Exception:
        return []

def get_upcoming():
    try:
        sql = """SELECT
                    P.id,
                    P.title as "title",
                    P.zip_code as "zip_code",
                    to_char(DATE(P.open_on)::date, 'DD.MM.YYYY') as "open_on",
                    to_char(DATE(P.close_on)::date, 'DD.MM.YYYY') as "close_on",
                    P.created_at,
                    U.id as "user_id",
                    U.name as "created_by",
                    P.open_on > CURRENT_DATE
                 FROM polls AS P
                 JOIN users AS U
                 ON U.id=P.created_by
                 WHERE
                    P.open_on > CURRENT_DATE
                    AND P.archived_at IS NULL
                 ORDER BY P.created_at DESC"""

        result = db.session.execute(text(sql))
        polls = result.fetchall()

        return polls

    except Exception:
        return []

def get_past():
    try:
        sql = """SELECT
                    P.id,
                    P.title as "title",
                    P.zip_code as "zip_code",
                    to_char(DATE(P.open_on)::date, 'DD.MM.YYYY') as "open_on",
                    to_char(DATE(P.close_on)::date, 'DD.MM.YYYY') as "close_on",
                    P.created_at,
                    U.id as "user_id",
                    U.name as "created_by",
                    P.close_on < CURRENT_DATE
                 FROM polls AS P
                 JOIN users AS U
                 ON U.id=P.created_by
                 WHERE
                    P.close_on < CURRENT_DATE
                    AND P.archived_at IS NULL
                 ORDER BY P.created_at DESC"""

        result = db.session.execute(text(sql))
        polls = result.fetchall()

        return polls

    except Exception:
        return []

def get_archived():
    try:
        sql = """SELECT
                    P.id,
                    P.title as "title",
                    P.zip_code as "zip_code",
                    to_char(DATE(P.open_on)::date, 'DD.MM.YYYY') as "open_on",
                    to_char(DATE(P.close_on)::date, 'DD.MM.YYYY') as "close_on",
                    P.created_at,
                    P.archived_at,
                    U.id as "user_id",
                    U.name as "created_by",
                    (SELECT name FROM users WHERE id=P.archived_by) as "archived_by"
                 FROM polls AS P
                 JOIN users AS U
                 ON U.id=P.created_by
                 WHERE P.archived_at IS NOT NULL
                 ORDER BY P.created_at DESC"""

        result = db.session.execute(text(sql))
        polls = result.fetchall()

        return polls

    except Exception:
        return []

def archive(user_id: int, poll_id: int):
    try:
        sql = """UPDATE polls
                 SET
                    archived_at=NOW(),
                    archived_by=:archived_by
                 WHERE id=:id"""

        values = {
            "archived_by": user_id,
            "id": poll_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def unarchive(user_id: int, poll_id: int):
    try:
        sql = """UPDATE polls
                 SET
                    archived_at=NULL,
                    archived_by=NULL
                 WHERE id=:id"""

        values = {
            "archived_by": user_id,
            "id": poll_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True
