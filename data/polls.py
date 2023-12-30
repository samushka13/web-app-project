from flask import session
from sqlalchemy.sql import text
from helpers.contants import ITEMS_PER_PAGE
from db import db

def add(title: str, zip_code: str, open_on: str, close_on: str):
    sql = """INSERT INTO polls
                (title, zip_code, open_on, close_on, created_at, created_by)
            VALUES
                (:title, :zip_code, :open_on, :close_on, NOW(), :created_by)
            RETURNING id"""

    values = {
        "title": title,
        "zip_code": zip_code,
        "open_on": open_on,
        "close_on": close_on,
        "created_by": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def get_current_count():
    sql = """SELECT COUNT(id)
            FROM polls
            WHERE
                open_on <= CURRENT_DATE
                AND close_on > CURRENT_DATE
                AND archived_at IS NULL"""

    result = db.session.execute(text(sql))

    return result.fetchone()[0]

def get_upcoming_count():
    sql = """SELECT COUNT(id)
            FROM polls
            WHERE
                open_on > CURRENT_DATE
                AND archived_at IS NULL"""

    result = db.session.execute(text(sql))
    db.session.commit()

    return result.fetchone()[0]

def get_past_count():
    sql = """SELECT COUNT(id)
            FROM polls
            WHERE
                close_on < CURRENT_DATE
                AND archived_at IS NULL"""

    result = db.session.execute(text(sql))

    return result.fetchone()[0]

def get_archived_count():
    sql = """SELECT COUNT(id)
            FROM polls
            WHERE archived_at IS NOT NULL"""

    result = db.session.execute(text(sql))

    return result.fetchone()[0]

def get_nearby_count():
    zip_code = session["zip_code"]

    sql = """SELECT COUNT(id)
            FROM polls
            WHERE
                open_on <= CURRENT_DATE
                AND close_on > CURRENT_DATE
                AND zip_code=:zip_code
                AND archived_at IS NULL"""

    values = {
        "zip_code": zip_code
    }

    result = db.session.execute(text(sql), values)

    return result.fetchone()[0]

def get_current(idx: int):
    sql = """SELECT
                id,
                title,
                zip_code,
                open_on,
                close_on,
                created_at
            FROM polls
            WHERE
                open_on <= CURRENT_DATE
                AND close_on > CURRENT_DATE
                AND archived_at IS NULL
            ORDER BY open_on DESC
            LIMIT :limit
            OFFSET :offset"""

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
                zip_code,
                open_on,
                close_on,
                created_at
            FROM polls
            WHERE
                open_on > CURRENT_DATE
                AND archived_at IS NULL
            ORDER BY open_on DESC
            LIMIT :limit
            OFFSET :offset"""

    values = {
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def get_past(idx: int):
    sql = """SELECT
                id,
                title,
                zip_code,
                open_on,
                close_on,
                created_at
            FROM polls
            WHERE
                close_on < CURRENT_DATE
                AND archived_at IS NULL
            ORDER BY open_on DESC
            LIMIT :limit
            OFFSET :offset"""

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
                zip_code,
                open_on,
                close_on,
                created_at,
                archived_at
            FROM polls
            WHERE archived_at IS NOT NULL
            ORDER BY open_on DESC
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
                zip_code,
                open_on,
                close_on,
                created_at
            FROM polls
            WHERE
                open_on <= CURRENT_DATE
                AND close_on > CURRENT_DATE
                AND zip_code=:zip_code
                AND archived_at IS NULL
            ORDER BY open_on DESC
            LIMIT :limit
            OFFSET :offset"""

    values = {
        "zip_code": session["zip_code"],
        "limit": ITEMS_PER_PAGE,
        "offset": idx * ITEMS_PER_PAGE
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()

def get_details(poll_id: int):
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
                V.for,
                V.against,
                V.user_for,
                V.user_against
            FROM
                (SELECT
                    COALESCE(SUM(CASE WHEN vote=True THEN 1 ELSE 0 END), 0)
                        as "for",
                    COALESCE(SUM(CASE WHEN vote=False THEN 1 ELSE 0 END), 0)
                        as "against",
                    COALESCE(SUM(CASE WHEN vote=True AND voted_by=:user_id THEN 1 ELSE 0 END), 0)
                        as "user_for",
                    COALESCE(SUM(CASE WHEN vote=False AND voted_by=:user_id THEN 1 ELSE 0 END), 0)
                        as "user_against"
                FROM
                    (SELECT DISTINCT
                        vote,
                        voted_by
                    FROM votes
                    WHERE poll_id=:poll_id) AS T) AS V,
                polls AS P
            JOIN users AS U
                ON U.id=P.created_by
            WHERE P.id=:poll_id"""

    values = {
        "poll_id": poll_id,
        "user_id": session["user_id"]
    }

    result = db.session.execute(text(sql), values)

    return result.fetchone()

def archive(poll_id: int):
    sql = """UPDATE polls
            SET
                archived_at=NOW(),
                archived_by=:archived_by
            WHERE id=:id
            RETURNING id"""

    values = {
        "archived_by": session["user_id"],
        "id": poll_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def unarchive(poll_id: int):
    sql = """UPDATE polls
            SET
                archived_at=NULL,
                archived_by=NULL
            WHERE id=:id
            RETURNING id"""

    values = {
        "id": poll_id
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def vote(poll_id: int, vote_type: bool):
    sql = """SELECT
                id,
                archived_at IS NOT NULL as "archived",
                close_on <= CURRENT_DATE as "past",
                open_on > CURRENT_DATE as "upcoming"
            FROM polls
            WHERE id=:id"""

    values = {
        "id": poll_id,
    }

    result = db.session.execute(text(sql), values)

    poll = result.fetchone()

    if not poll:
        return None

    if poll[1]:
        return "archived-poll"

    if poll[2]:
        return "past-poll"

    if poll[3]:
        return "upcoming-poll"

    sql = """INSERT INTO votes
                (poll_id, vote, voted_at, voted_by)
            VALUES
                (:poll_id, :vote, NOW(), :voted_by)
            RETURNING id"""

    values = {
        "poll_id": poll_id,
        "vote": vote_type,
        "voted_by": session["user_id"]
    }

    result = db.session.execute(text(sql), values)
    db.session.commit()

    return result.fetchone()

def get_votes_by_gender(poll_id: int):
    sql = """SELECT
                COALESCE(SUM(CASE WHEN vote=True AND gender='female' THEN 1 ELSE 0 END), 0)
                    as "females_for",
                COALESCE(SUM(CASE WHEN vote=False AND gender='female' THEN 1 ELSE 0 END), 0)
                    as "females_against",
                COALESCE(SUM(CASE WHEN vote=True AND gender='male' THEN 1 ELSE 0 END), 0)
                    as "males_for",
                COALESCE(SUM(CASE WHEN vote=False AND gender='male' THEN 1 ELSE 0 END), 0)
                    as "males_against",
                COALESCE(SUM(CASE WHEN vote=True AND gender='other' THEN 1 ELSE 0 END), 0)
                    as "others_for",
                COALESCE(SUM(CASE WHEN vote=False AND gender='other' THEN 1 ELSE 0 END), 0)
                    as "others_against",
                COALESCE(SUM(CASE WHEN vote=True AND gender IS NULL THEN 1 ELSE 0 END), 0)
                    as "nones_for",
                COALESCE(SUM(CASE WHEN vote=False AND gender IS NULL THEN 1 ELSE 0 END), 0)
                    as "nones_against"
            FROM
                (SELECT DISTINCT
                    U.gender,
                    V.vote,
                    V.voted_by
                FROM votes AS V
                JOIN users AS U
                    ON U.id=V.voted_by
                WHERE V.poll_id=:poll_id) AS T"""

    values = {
        "poll_id": poll_id
    }

    result = db.session.execute(text(sql), values)

    return result.fetchone()

def get_votes_by_age_group(poll_id: int):
    sql = """SELECT
                COALESCE(SUM(CASE WHEN vote=True AND age < 30 THEN 1 ELSE 0 END), 0)
                    as "group_1_for",
                COALESCE(SUM(CASE WHEN vote=False AND age < 30 THEN 1 ELSE 0 END), 0)
                    as "group_1_against",
                COALESCE(SUM(CASE WHEN vote=True AND age BETWEEN 30 AND 40 THEN 1 ELSE 0 END), 0)
                    as "group_2_for",
                COALESCE(SUM(CASE WHEN vote=False AND age BETWEEN 30 AND 40 THEN 1 ELSE 0 END), 0)
                    as "group_2_against",
                COALESCE(SUM(CASE WHEN vote=True AND age BETWEEN 40 AND 50 THEN 1 ELSE 0 END), 0)
                    as "group_3_for",
                COALESCE(SUM(CASE WHEN vote=False AND age BETWEEN 40 AND 50 THEN 1 ELSE 0 END), 0)
                    as "group_3_against",
                COALESCE(SUM(CASE WHEN vote=True AND age BETWEEN 50 AND 60 THEN 1 ELSE 0 END), 0)
                    as "group_4_for",
                COALESCE(SUM(CASE WHEN vote=False AND age BETWEEN 50 AND 60 THEN 1 ELSE 0 END), 0)
                    as "group_4_against",
                COALESCE(SUM(CASE WHEN vote=True AND age > 60 THEN 1 ELSE 0 END), 0)
                    as "group_5_for",
                COALESCE(SUM(CASE WHEN vote=False AND age > 60 THEN 1 ELSE 0 END), 0)
                    as "group_5_against",
                COALESCE(SUM(CASE WHEN vote=True AND age IS NULL THEN 1 ELSE 0 END), 0)
                    as "group_none_for",
                COALESCE(SUM(CASE WHEN vote=False AND age IS NULL THEN 1 ELSE 0 END), 0)
                    as "group_none_against"
            FROM
                (SELECT DISTINCT
                    DATE_PART('year', AGE(date_of_birth)) as "age",
                    V.vote,
                    V.voted_by
                FROM votes AS V
                JOIN users AS U
                    ON U.id=V.voted_by
                WHERE V.poll_id=:poll_id) AS T"""

    values = {
        "poll_id": poll_id
    }

    result = db.session.execute(text(sql), values)

    return result.fetchone()

def get_votes_by_zip_code(poll_id: int):
    sql = """SELECT
                zip_code,
                COALESCE(SUM(CASE WHEN vote=True THEN 1 ELSE 0 END), 0) as "for",
                COALESCE(SUM(CASE WHEN vote=False THEN 1 ELSE 0 END), 0) as "against"
            FROM
                (SELECT DISTINCT
                    V.vote,
                    V.voted_by,
                    U.zip_code
                FROM votes AS V
                JOIN users AS U
                    ON U.id=V.voted_by
                WHERE poll_id=:poll_id) AS T
            GROUP BY zip_code
            ORDER BY zip_code"""

    values = {
        "poll_id": poll_id
    }

    result = db.session.execute(text(sql), values)

    return result.fetchall()
