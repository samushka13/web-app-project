from datetime import datetime
from helpers.contants import (
    DATE_LENGTH,
    TITLE_MIN_LENGTH,
    TITLE_MAX_LENGTH,
    BODY_MAX_LENGTH,
    ZIP_CODE_LENGTH
)

def username_too_short(username: str):
    return len(username) < 6

def username_too_long(username: str):
    return len(username) > 50

def password_too_short(password: str):
    return len(password) < 6

def date_format_too_short(date: str):
    return len(date) < DATE_LENGTH

def invalid_optional_date(date: str):
    return bool(date) and date_format_too_short(date)

def invalid_required_date(date: str):
    return not date or date_format_too_short(date)

def invalid_zip_code(zip_code: str):
    return bool(zip_code) and (len(zip_code) != ZIP_CODE_LENGTH or not zip_code.isdigit())

def invalid_street_address(street_address: str):
    return bool(street_address) and street_address.isdigit()

def title_too_short(title: str):
    return len(title) < TITLE_MIN_LENGTH

def title_too_long(title: str):
    return len(title) > TITLE_MAX_LENGTH

def body_too_long(body: str):
    return bool(body) and len(body) > BODY_MAX_LENGTH

def start_date_after_end_date(start: str, end: str):
    return datetime.strptime(start, "%Y-%m-%d") > datetime.strptime(end, "%Y-%m-%d")
