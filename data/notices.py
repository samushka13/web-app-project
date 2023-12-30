from flask import session
from sqlalchemy.sql import text
from helpers.contants import ITEMS_PER_PAGE
from db import db

def add(title: str, body: str, zip_code: str, street_address: str):
    sql = """INSERT INTO notices
                (title, body, zip_code, street_address, created_at, created_by)
            VALUES
                (:title, :body, :zip_code, :street_address, NOW(), :created_by)
            RETURNING id"""

    values = {
        "title": title,
        "body": body,
        "zip_code": zip_code,
        "street_address": street_address,
        "created_by": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def get_all_count():
    sql = """SELECT COUNT(id)
            FROM notices
            WHERE archived_at IS NULL"""

    result = db.session.execute(text(sql))

    return result.fetchone()[0]

def get_created_by_user_count():
    sql = """SELECT COUNT(id)
            FROM notices
            WHERE
                created_by=:user_id
                AND archived_at IS NULL"""

    values = {
        "user_id": session["user_id"]
    }

    result = db.session.execute(text(sql), values)

    return result.fetchone()[0]

def get_archived_count():
    sql = """SELECT COUNT(id)
            FROM notices
            WHERE archived_at IS NOT NULL"""

    result = db.session.execute(text(sql))

    return result.fetchone()[0]

def get_nearby_count():
    sql = """SELECT COUNT(id)
            FROM notices
            WHERE
                archived_at IS NULL
                AND zip_code=:zip_code"""

    values = {
        "zip_code": session["zip_code"]
    }

    result = db.session.execute(text(sql), values)

    return result.fetchone()[0]

def get_all(idx: int):
    sql = """SELECT
                id,
                title,
                body,
                zip_code,
                street_address,
                created_at
            FROM notices
            WHERE archived_at IS NULL
            ORDER BY created_at DESC
            LIMIT :limit
            OFFSET :offset"""

    values = {
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def get_created_by_user(idx: int):
    sql = """SELECT
                id,
                title,
                body,
                zip_code,
                street_address,
                created_at
            FROM notices
            WHERE
                created_by=:user_id
                AND archived_at IS NULL
            ORDER BY created_at DESC
            LIMIT :limit
            OFFSET :offset"""

    values = {
        "user_id": session["user_id"],
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
                street_address,
                created_at,
                archived_at
            FROM notices
            WHERE archived_at IS NOT NULL
            ORDER BY created_at DESC
            LIMIT :limit
            OFFSET :offset"""

    values = {
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def get_nearby(idx: int):
    sql = """SELECT
                id,
                title,
                body,
                zip_code,
                street_address,
                created_at
            FROM notices
            WHERE
                archived_at IS NULL
                AND zip_code=:zip_code
            ORDER BY created_at DESC
            LIMIT :limit
            OFFSET :offset"""

    values = {
        "zip_code": session["zip_code"],
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def get_details(notice_id: int):
    sql = """SELECT
                N.id,
                N.title,
                N.body,
                N.zip_code,
                N.street_address,
                N.created_at,
                N.archived_at,
                U.id as "user_id",
                U.name as "created_by",
                (SELECT name FROM users WHERE id=N.archived_by) as "archived_by",
                V.total_views,
                V.unique_views,
                S.total_supports,
                S.unique_supports
            FROM
                (SELECT
                    COUNT(viewed_by) as "total_views",
                    COUNT(DISTINCT viewed_by) as "unique_views"
                FROM notice_views
                WHERE notice_id=:notice_id) AS V,
                (SELECT
                    COUNT(supported_by) as "total_supports",
                    COUNT(DISTINCT supported_by) as "unique_supports"
                FROM notice_supports
                WHERE notice_id=:notice_id) AS S,
                notices AS N
            JOIN users AS U
                ON U.id=N.created_by
            WHERE N.id=:notice_id"""

    values = {
        "notice_id": notice_id
    }

    result = db.session.execute(text(sql), values)

    return result.fetchone()

def archive(notice_id: int):
    sql = """UPDATE notices
            SET
                archived_at=NOW(),
                archived_by=:archived_by
            WHERE id=:id
            RETURNING id"""

    values = {
        "archived_by": session["user_id"],
        "id": notice_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def unarchive(notice_id: int):
    sql = """UPDATE notices
            SET
                archived_at=NULL,
                archived_by=NULL
            WHERE id=:id
            RETURNING id"""

    values = {
        "id": notice_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def add_view(notice_id: int):
    sql = """INSERT INTO notice_views
                (notice_id, viewed_at, viewed_by)
            VALUES
                (:notice_id, NOW(), :viewed_by)
            RETURNING id"""

    values = {
        "notice_id": notice_id,
        "viewed_by": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def add_support(notice_id: int):
    sql = """INSERT INTO notice_supports
                (notice_id, supported_at, supported_by)
            VALUES
                (:notice_id, NOW(), :supported_by)
            RETURNING id"""

    values = {
        "notice_id": notice_id,
        "supported_by": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def add_status(user_id: int, notice_id: int, status: str):
    sql = """INSERT INTO notice_statuses
                (notice_id, status, set_at, set_by)
            VALUES
                (:notice_id, :status, NOW(), :set_by)
            RETURNING id"""

    values = {
        "notice_id": notice_id,
        "status": status,
        "set_by": user_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def acknowledge(notice_id: int):
    return add_status(session["user_id"], notice_id, "read")

def wip(notice_id: int):
    return add_status(session["user_id"], notice_id, "wip")

def done(notice_id: int):
    return add_status(session["user_id"], notice_id, "done")

def get_statuses(notice_id: int):
    sql = """SELECT
                N.id,
                N.notice_id,
                N.status,
                N.set_at,
                U.name as "set_by"
            FROM notice_statuses AS N
            JOIN users AS U
                ON U.id=N.set_by
            WHERE N.notice_id=:notice_id
            ORDER BY N.set_at ASC"""

    values = {
        "notice_id": notice_id
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def delete_status(status_id: int):
    sql = """DELETE FROM notice_statuses
            WHERE id=:id
            RETURNING id"""

    values = {
        "id": status_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()
