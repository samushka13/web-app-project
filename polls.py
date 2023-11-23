from sqlalchemy.sql import text
from db import db

def get_all():
    sql = """SELECT
                P.id,
                P.title,
                P.zip_code,
                to_char(DATE(open_on)::date, 'DD.MM.YYYY'),
                to_char(DATE(close_on)::date, 'DD.MM.YYYY'),
                U.id,
                U.name as "created_by"
             FROM polls AS P
             JOIN users AS U
             ON U.id=P.created_by"""

    result = db.session.execute(text(sql))
    users = result.fetchall()

    return users
