from flask import session
from sqlalchemy.sql import text
from db import db

def add(title: str, zip_code: str, open_on: str, close_on: str):
    try:
        user_id = session["user_id"]

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
                 ORDER BY P.open_on DESC"""

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
                 ORDER BY P.open_on DESC"""

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
                 ORDER BY P.open_on DESC"""

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
                 ORDER BY P.open_on DESC"""

        result = db.session.execute(text(sql))
        polls = result.fetchall()

        return polls

    except Exception:
        return []

def get_nearby():
    try:
        zip_code = session["zip_code"]

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
                    AND P.zip_code=:zip_code
                 ORDER BY P.open_on DESC"""

        values = {
            "zip_code": zip_code
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

def archive(poll_id: int):
    try:
        user_id = session["user_id"]

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

def unarchive(poll_id: int):
    try:
        sql = """UPDATE polls
                 SET
                    archived_at=NULL,
                    archived_by=NULL
                 WHERE id=:id"""

        values = {
            "id": poll_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True

def vote(poll_id: int, vote_type: bool):
    try:
        user_id = session["user_id"]

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

def get_poll_title(poll_id: int):
    try:
        sql = """SELECT title
                 FROM polls
                 WHERE id=:poll_id"""

        values = {
            "poll_id": poll_id
        }

        result = db.session.execute(text(sql), values)
        poll_title = result.fetchone()

        return poll_title

    except Exception:
        return False

def get_votes_by_gender(poll_id: int):
    try:
        sql = """SELECT
                    females_for,
                    females_against,
                    males_for,
                    males_against,
                    others_for,
                    others_against,
                    no_genders_for,
                    no_genders_against
                 FROM
                 (SELECT COUNT(DISTINCT U.id) AS females_for
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True AND U.gender='female')
                    AS females_for,
                 (SELECT COUNT(DISTINCT U.id) AS females_against
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False AND U.gender='female')
                    AS females_against,
                 (SELECT COUNT(DISTINCT U.id) AS males_for
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True AND U.gender='male')
                    AS males_for,
                 (SELECT COUNT(DISTINCT U.id) AS males_against
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False AND U.gender='male')
                    AS males_against,
                 (SELECT COUNT(DISTINCT U.id) AS others_for
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True AND U.gender='other')
                    AS others_for,
                 (SELECT COUNT(DISTINCT U.id) AS others_against
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False AND U.gender='other')
                    AS others_against,
                 (SELECT COUNT(DISTINCT U.id) AS no_genders_for
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True AND U.gender IS NULL)
                    AS no_genders_for,
                 (SELECT COUNT(DISTINCT U.id) AS no_genders_against
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False AND U.gender IS NULL)
                    AS no_genders_against"""

        values = {
            "poll_id": poll_id
        }

        result = db.session.execute(text(sql), values)
        votes_by_gender = result.fetchone()

        return votes_by_gender

    except Exception:
        return False

def get_votes_by_age_group(poll_id: int):
    try:
        sql = """SELECT
                    group_1_for,
                    group_1_against,
                    group_2_for,
                    group_2_against,
                    group_3_for,
                    group_3_against,
                    group_4_for,
                    group_4_against,
                    group_5_for,
                    group_5_against,
                    no_group_for,
                    no_group_against
                 FROM
                 (SELECT COUNT(DISTINCT U.id) AS group_1_for
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True AND DATE_PART('year', AGE(U.date_of_birth)) < 30)
                    AS group_1_for,
                 (SELECT COUNT(DISTINCT U.id) AS group_1_against
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False AND DATE_PART('year', AGE(U.date_of_birth)) < 30)
                    AS group_1_against,
                 (SELECT COUNT(DISTINCT U.id) AS group_2_for
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True AND (DATE_PART('year', AGE(U.date_of_birth)) BETWEEN 30 AND 40))
                    AS group_2_for,
                 (SELECT COUNT(DISTINCT U.id) AS group_2_against
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False AND (DATE_PART('year', AGE(U.date_of_birth)) BETWEEN 30 AND 40))
                    AS group_2_against,
                 (SELECT COUNT(DISTINCT U.id) AS group_3_for
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True AND (DATE_PART('year', AGE(U.date_of_birth)) BETWEEN 40 AND 50))
                    AS group_3_for,
                 (SELECT COUNT(DISTINCT U.id) AS group_3_against
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False AND (DATE_PART('year', AGE(U.date_of_birth)) BETWEEN 40 AND 50))
                    AS group_3_against,
                 (SELECT COUNT(DISTINCT U.id) AS group_4_for
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True AND (DATE_PART('year', AGE(U.date_of_birth)) BETWEEN 50 AND 60))
                    AS group_4_for,
                 (SELECT COUNT(DISTINCT U.id) AS group_4_against
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False AND (DATE_PART('year', AGE(U.date_of_birth)) BETWEEN 50 AND 60))
                    AS group_4_against,
                 (SELECT COUNT(DISTINCT U.id) AS group_5_for
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True AND DATE_PART('year', AGE(U.date_of_birth)) > 60)
                    AS group_5_for,
                 (SELECT COUNT(DISTINCT U.id) AS group_5_against
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False AND DATE_PART('year', AGE(U.date_of_birth)) > 60)
                    AS group_5_against,
                 (SELECT COUNT(DISTINCT U.id) AS no_group_for
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True AND U.date_of_birth IS NULL)
                    AS no_group_for,
                 (SELECT COUNT(DISTINCT U.id) AS no_group_against
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False AND U.date_of_birth IS NULL)
                    AS no_group_against"""

        values = {
            "poll_id": poll_id
        }

        result = db.session.execute(text(sql), values)
        votes_by_age_group = result.fetchone()

        return votes_by_age_group

    except Exception:
        return False

def get_votes_by_zip_code(poll_id: int):
    try:
        sql = """SELECT
                    T1.zip_code,
                    T1.count AS "for",
                    T2.count AS "against"
                 FROM
                    (SELECT
                        COUNT(DISTINCT V.voted_by),
                        U.zip_code
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=True
                    GROUP BY U.zip_code) AS T1
                 FULL OUTER JOIN
                    (SELECT
                        COUNT(DISTINCT V.voted_by),
                        U.zip_code
                    FROM votes AS V
                    JOIN users AS U
                    ON U.id=V.voted_by
                    WHERE poll_id=:poll_id AND V.vote=False
                    GROUP BY U.zip_code) AS T2
                 ON T1.zip_code=T2.zip_code
                 """

        values = {
            "poll_id": poll_id
        }

        result = db.session.execute(text(sql), values)
        votes_by_zip_code = result.fetchall()

        return votes_by_zip_code

    except Exception:
        return False
