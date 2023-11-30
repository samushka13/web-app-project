from flask import request, session
from helpers.contants import GENDERS, DATE_LENGTH

def csrf_check_passed():
    return session["csrf_token"] == request.form["csrf_token"]

def get_date(date_value: str):
    date = None

    if date_value in request.form and len(request.form[date_value]) >= DATE_LENGTH:
        date = request.form[date_value]

    return date

def get_date_of_birth():
    return get_date("date_of_birth")

def get_gender():
    gender = None

    if "gender" in request.form and request.form["gender"] in GENDERS:
        gender = request.form["gender"]

    return gender

def get_zip_code():
    zip_code = None

    if "zip_code" in request.form and request.form["zip_code"] != "":
        zip_code = request.form["zip_code"]

    return zip_code

def get_admin_status():
    is_admin = False

    if "is_admin" in request.form:
        is_admin = request.form["is_admin"] == "yes"

    return is_admin

def get_body():
    body = None

    if "body" in request.form and request.form["body"] != "":
        body = request.form["body"]

    return body

def get_street_address():
    street_address = None

    if "street_address" in request.form and request.form["street_address"] != "":
        street_address = request.form["street_address"]

    return street_address
