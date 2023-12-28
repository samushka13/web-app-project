from flask import session
from sqlalchemy.sql import text
from helpers.contants import ITEMS_PER_PAGE
from db import db

def send(title: str, body: str):
    sql = """INSERT INTO feedbacks
                (title, body, sent_at, sent_by)
            VALUES
                (:title, :body, NOW(), :sent_by)
            RETURNING id"""

    values = {
        "title": title,
        "body": body,
        "sent_by": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def get_new_count():
    sql = """SELECT COUNT(id)
            FROM feedbacks
            WHERE
                acknowledged_at IS NULL
                AND archived_at IS NULL"""

    result = db.session.execute(text(sql))
    db.session.commit()

    return result.fetchone()[0]

def get_acknowledged_count():
    sql = """SELECT COUNT(id)
            FROM feedbacks
            WHERE
                acknowledged_at IS NOT NULL
                AND archived_at IS NULL"""

    result = db.session.execute(text(sql))
    db.session.commit()

    return result.fetchone()[0]

def get_archived_count():
    sql = """SELECT COUNT(id)
            FROM feedbacks
            WHERE archived_at IS NOT NULL"""

    result = db.session.execute(text(sql))
    db.session.commit()

    return result.fetchone()[0]

def get_new(idx: int):
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
            ORDER BY F.sent_at DESC
            LIMIT (:limit)
            OFFSET (:offset)"""

    values = {
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def get_acknowledged(idx: int):
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
            ORDER BY F.sent_at DESC
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
            ORDER BY F.sent_at DESC
            LIMIT (:limit)
            OFFSET (:offset)"""

    values = {
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def acknowledge(feedback_id: int):
    sql = """UPDATE feedbacks
            SET
                acknowledged_at=NOW(),
                acknowledged_by=:acknowledged_by
            WHERE id=:id
            RETURNING id"""

    values = {
        "acknowledged_by": session["user_id"],
        "id": feedback_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def unacknowledge(feedback_id: int):
    sql = """UPDATE feedbacks
            SET
                acknowledged_at=NULL,
                acknowledged_by=NULL
            WHERE
                id=:id
                AND archived_at IS NULL
            RETURNING id"""

    values = {
        "acknowledged_by": session["user_id"],
        "id": feedback_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def archive(feedback_id: int):
    sql = """UPDATE feedbacks
            SET
                archived_at=NOW(),
                archived_by=:archived_by
            WHERE id=:id
            RETURNING id"""

    values = {
        "archived_by": session["user_id"],
        "id": feedback_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def unarchive(feedback_id: int):
    sql = """UPDATE feedbacks
            SET
                archived_at=NULL,
                archived_by=NULL
            WHERE id=:id
            RETURNING id"""

    values = {
        "id": feedback_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()
