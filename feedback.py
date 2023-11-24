from sqlalchemy.sql import text
from db import db

def send(user_id: int, title: str, body: str):
    try:
        sql = """INSERT INTO feedbacks (title, body, sent_at, sent_by)
                 VALUES (:title, :body, NOW(), :sent_by)"""

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

def get_all():
    sql = """SELECT
                F.id, F.title, F.body, F.sent_at, F.acknowledged_at, F.acknowledged_by, F.archived_at, F.archived_by,
                U.id, U.name as "sent_by"
             FROM feedbacks AS F
             JOIN users AS U
             ON U.id=F.sent_by"""

    result = db.session.execute(text(sql))
    feedbacks = result.fetchall()

    return feedbacks
