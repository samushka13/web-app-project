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
                    P.title,
                    P.zip_code,
                    P.open_on,
                    P.close_on,
                    P.created_at
                 FROM polls AS P
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
                    P.title,
                    P.zip_code,
                    P.open_on,
                    P.close_on,
                    P.created_at
                 FROM polls AS P
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
                    P.title,
                    P.zip_code,
                    P.open_on,
                    P.close_on,
                    P.created_at
                 FROM polls AS P
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
                    P.title,
                    P.zip_code,
                    P.open_on,
                    P.close_on,
                    P.created_at,
                    P.archived_at
                 FROM polls AS P
                 WHERE P.archived_at IS NOT NULL
                 ORDER BY P.created_at DESC"""

        result = db.session.execute(text(sql))
        polls = result.fetchall()

        return polls

    except Exception:
        return []

def get_nearby(user_zip_code: str):
    try:
        sql = """SELECT
                    P.id,
                    P.title,
                    P.zip_code,
                    P.open_on,
                    P.close_on,
                    P.created_at
                 FROM polls AS P
                 WHERE
                    P.archived_at IS NULL
                    AND P.zip_code=:user_zip_code
                 ORDER BY P.created_at DESC"""

        values = {
            "user_zip_code": user_zip_code
        }

        result = db.session.execute(text(sql), values)
        polls = result.fetchall()

        return polls

    except Exception:
        return []

def get_details(poll_id: int):
    try:
        sql = """SELECT
                    P.id,
                    P.title,
                    P.zip_code,
                    P.open_on,
                    P.close_on,
                    P.created_at,
                    P.archived_at,
                    U.id as "user_id",
                    U.name as "created_by",
                    (SELECT name FROM users WHERE id=P.archived_by) as "archived_by",
                    (SELECT COUNT(DISTINCT voted_by) FROM votes WHERE poll_id=:poll_id AND vote=True) as "for",
                    (SELECT COUNT(DISTINCT voted_by) FROM votes WHERE poll_id=:poll_id AND vote=False) as "against"
                 FROM polls AS P
                 JOIN users AS U
                 ON U.id=P.created_by
                 WHERE P.id=:poll_id"""

        values = {
            "poll_id": poll_id
        }

        result = db.session.execute(text(sql), values)
        item = result.fetchone()

        return item

    except Exception:
        return False

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

def vote(poll_id: int, user_id: int, vote_type: bool):
    try:
        sql = """INSERT INTO votes
                    (poll_id, vote, voted_at, voted_by)
                 VALUES
                    (:poll_id, :vote, NOW(), :voted_by)"""

        values = {
            "poll_id": poll_id,
            "vote": vote_type,
            "voted_by": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True
