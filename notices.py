from sqlalchemy.sql import text
from db import db

def get_all():
    sql = """SELECT
                N.id, N.title, N.body, N.zip_code, N.street_address, N.created_at,
                U.id, U.name as "created_by"
             FROM notices AS N
             JOIN users AS U
             ON U.id=N.created_by"""

    result = db.session.execute(text(sql))
    users = result.fetchall()

    return users
