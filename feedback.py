from datetime import datetime
from sqlalchemy.sql import text
from db import db

def send(user_id: int, title: str, body: str):
    sent_at = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

    try:
        sql = """INSERT INTO feedbacks (title, body, sent_at, sent_by)
                 VALUES (:title, :body, :sent_at, :sent_by)"""

        values = {
            "title": title,
            "body": body,
            "sent_at": sent_at,
            "sent_by": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True
