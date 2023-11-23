from sqlalchemy.sql import text
from db import db

def add(user_id: int, title: str, body: str, zip_code: str, publish_on: str):
    try:
        sql = """INSERT INTO news (title, body, zip_code, publish_on, created_at, created_by)
                 VALUES (:title, :body, :zip_code, :publish_on, NOW(), :created_by)"""

        values = {
            "title": title,
            "body": body,
            "zip_code": zip_code,
            "publish_on": publish_on,
            "created_by": user_id
        }

        db.session.execute(text(sql), values)
        db.session.commit()

    except Exception:
        return False

    return True
