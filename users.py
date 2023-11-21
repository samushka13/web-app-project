from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash
from db import db

def register(name, password, date_of_birth, gender, zip_code, admin):
    hash_value = generate_password_hash(password)

    try:
        sql = """INSERT INTO users (name, password, date_of_birth, gender, zip_code, admin)
                 VALUES (:name, :password, :date_of_birth, :gender, :zip_code, :admin)"""

        new_user = {
            "name":name,
            "password":hash_value,
            "date_of_birth":date_of_birth,
            "gender":gender,
            "zip_code":zip_code,
            "admin":admin
        }

        db.session.execute(text(sql), new_user)
        db.session.commit()

    except Exception:
        return False

    return True
