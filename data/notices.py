from sqlalchemy.sql import text
from db import db

def add(user_id: int, title: str, body: str, zip_code: str, street_address: str):
    try:
        sql = """INSERT INTO notices
                    (title, body, zip_code, street_address, created_at, created_by)
                 VALUES
                    (:title, :body, :zip_code, :street_address, NOW(), :created_by)"""

        values = {
            "title": title,
            "body": body,
            "zip_code": zip_code,
            "street_address": street_address,
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
                    N.id,
                    N.title,
                    N.body,
                    N.zip_code,
                    N.street_address,
                    N.created_at
                 FROM notices AS N
                 WHERE N.archived_at IS NULL
                 ORDER BY N.created_at DESC"""

        result = db.session.execute(text(sql))
        notices = result.fetchall()

        return notices

    except Exception:
        return []

def get_user_notices(user_id: int):
    try:
        sql = """SELECT
                    N.id,
                    N.title,
                    N.body,
                    N.zip_code,
                    N.street_address,
                    N.created_at
                 FROM notices AS N
                 WHERE :user_id=N.created_by
                 ORDER BY N.created_at DESC"""

        values = {
            "user_id": user_id
        }

        result = db.session.execute(text(sql), values)
        notices = result.fetchall()

        return notices

    except Exception:
        return []

def get_archived():
    try:
        sql = """SELECT
                    N.id,
                    N.title,
                    N.body,
                    N.zip_code,
                    N.street_address,
                    N.created_at,
                    N.archived_at
                 FROM notices AS N
                 WHERE N.archived_at IS NOT NULL
                 ORDER BY N.created_at DESC"""

        result = db.session.execute(text(sql))
        notices = result.fetchall()

        return notices

    except Exception:
        return []

def get_nearby(user_zip_code: str):
    try:
        sql = """SELECT
                    N.id,
                    N.title,
                    N.body,
                    N.zip_code,
                    N.street_address,
                    N.created_at
                 FROM notices AS N
                 WHERE
                    N.archived_at IS NULL
                    AND N.zip_code=:user_zip_code
                 ORDER BY N.created_at DESC"""

        values = {
            "user_zip_code": user_zip_code
        }

        result = db.session.execute(text(sql), values)
        news = result.fetchall()

        return news

    except Exception:
        return []

def get_details(notice_id: int):
    try:
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
                    (SELECT COUNT(viewed_by) FROM notice_views WHERE notice_id=:notice_id) as "total_views",
                    (SELECT COUNT(DISTINCT viewed_by) FROM notice_views WHERE notice_id=:notice_id) as "unique_views",
                    (SELECT COUNT(supported_by) FROM notice_supports WHERE notice_id=:notice_id) as "total_supports",
                    (SELECT COUNT(DISTINCT supported_by) FROM notice_supports WHERE notice_id=:notice_id) as "unique_supports"
                 FROM notices AS N
                 JOIN users AS U
                 ON U.id=N.created_by
                 WHERE N.id=:notice_id"""

        values = {
            "notice_id": notice_id
        }

        result = db.session.execute(text(sql), values)
        item = result.fetchone()

        return item

    except Exception:
        return False

def archive(user_id: int, notice_id: int):
    try:
        sql = """UPDATE notices
                 SET
                    archived_at=NOW(),
                    archived_by=:archived_by
                 WHERE id=:id"""

        values = {
            "archived_by": user_id,
            "id": notice_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def unarchive(user_id: int, notice_id: int):
    try:
        sql = """UPDATE notices
                 SET
                    archived_at=NULL,
                    archived_by=NULL
                 WHERE id=:id"""

        values = {
            "archived_by": user_id,
            "id": notice_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def add_view(notice_id: int, user_id: int):
    try:
        sql = """INSERT INTO notice_views
                    (notice_id, viewed_at, viewed_by)
                 VALUES
                    (:notice_id, NOW(), :viewed_by)"""

        values = {
            "notice_id": notice_id,
            "viewed_by": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def add_support(notice_id: int, user_id: int):
    try:
        sql = """INSERT INTO notice_supports
                    (notice_id, supported_at, supported_by)
                 VALUES
                    (:notice_id, NOW(), :supported_by)"""

        values = {
            "notice_id": notice_id,
            "supported_by": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def add_status(user_id: int, notice_id: int, status: str):
    try:
        sql = """INSERT INTO notice_statuses
                    (notice_id, status, set_at, set_by)
                 VALUES
                    (:notice_id, :status, NOW(), :set_by)"""

        values = {
            "notice_id": notice_id,
            "status": status,
            "set_by": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def acknowledge(user_id: int, notice_id: int):
    return add_status(user_id, notice_id, "read")

def wip(user_id: int, notice_id: int):
    return add_status(user_id, notice_id, "wip")

def done(user_id: int, notice_id: int):
    return add_status(user_id, notice_id, "done")

def get_statuses(notice_id: int):
    try:
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
        statuses = result.fetchall()

        return statuses

    except Exception:
        return []
