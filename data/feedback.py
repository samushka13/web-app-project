from flask import session
from sqlalchemy.sql import text
from db import db

def send(title: str, body: str):
    try:
        user_id = session["user_id"]

        sql = """INSERT INTO feedbacks
                    (title, body, sent_at, sent_by)
                 VALUES
                    (:title, :body, NOW(), :sent_by)"""

        values = {
            "title": title,
            "body": body,
            "sent_by": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def get_new():
    try:
        sql = """SELECT
                    F.id,
                    F.title,
                    F.body,
                    F.sent_at,
                    U.id as "user_id",
                    U.name as "sent_by"
                 FROM feedbacks AS F
                 JOIN users AS U
                 ON U.id=F.sent_by
                 WHERE 
                    F.acknowledged_at IS NULL
                    AND F.archived_at IS NULL
                 ORDER BY F.sent_at DESC"""

        result = db.session.execute(text(sql))
        feedbacks = result.fetchall()

        return feedbacks

    except Exception:
        return False

def get_acknowledged():
    try:
        sql = """SELECT
                    F.id,
                    F.title,
                    F.body,
                    F.sent_at,
                    F.acknowledged_at,
                    (SELECT name FROM users WHERE id=F.acknowledged_by) as "acknowledged_by",
                    U.id as "user_id",
                    U.name as "sent_by"
                 FROM feedbacks AS F
                 JOIN users AS U
                 ON U.id=F.sent_by
                 WHERE
                    F.acknowledged_at IS NOT NULL
                    AND F.archived_at IS NULL
                 ORDER BY F.sent_at DESC"""

        result = db.session.execute(text(sql))
        feedbacks = result.fetchall()

        return feedbacks

    except Exception:
        return False

def get_archived():
    try:
        sql = """SELECT
                    F.id,
                    F.title,
                    F.body,
                    F.sent_at,
                    F.acknowledged_at,
                    (SELECT name FROM users WHERE id=F.acknowledged_by) as "acknowledged_by",
                    F.archived_at,
                    U.id as "user_id",
                    U.name as "sent_by",
                    (SELECT name FROM users WHERE id=F.archived_by) as "archived_by"
                 FROM feedbacks AS F
                 JOIN users AS U
                 ON U.id=F.sent_by
                 WHERE F.archived_at IS NOT NULL
                 ORDER BY F.sent_at DESC"""

        result = db.session.execute(text(sql))
        feedbacks = result.fetchall()

        return feedbacks

    except Exception:
        return False

def acknowledge(feedback_id: int):
    try:
        user_id = session["user_id"]

        sql = """UPDATE feedbacks
                 SET
                    acknowledged_at=NOW(),
                    acknowledged_by=:acknowledged_by
                 WHERE id=:id"""

        values = {
            "acknowledged_by": user_id,
            "id": feedback_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def unacknowledge(feedback_id: int):
    try:
        user_id = session["user_id"]

        sql = """UPDATE feedbacks
                 SET
                    acknowledged_at=NULL,
                    acknowledged_by=NULL
                 WHERE id=:id"""

        values = {
            "acknowledged_by": user_id,
            "id": feedback_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def archive(feedback_id: int):
    try:
        user_id = session["user_id"]

        sql = """UPDATE feedbacks
                 SET
                    archived_at=NOW(),
                    archived_by=:archived_by
                 WHERE id=:id"""

        values = {
            "archived_by": user_id,
            "id": feedback_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def unarchive(feedback_id: int):
    try:
        sql = """UPDATE feedbacks
                 SET
                    archived_at=NULL,
                    archived_by=NULL
                 WHERE id=:id"""

        values = {
            "id": feedback_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True
