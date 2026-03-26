from flask import request, make_response
import mysql.connector
import re #this library is the shortcut for regular expressions, also called Regex
import os
from datetime import datetime
from functools import wraps

############################## connect to database
def db():
    try:
        db_host = os.getenv("DB_HOST", "mariadb")
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "password")
        db_name = os.getenv("DB_NAME", "adamsfaktura")
        db_port = int(os.getenv("DB_PORT", "3306"))
        db_ssl_disabled = os.getenv("DB_SSL_DISABLED", "true").lower() == "true"

        db = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            ssl_disabled=db_ssl_disabled
        )
        cursor = db.cursor(dictionary=True)
        return db, cursor
    except Exception as e:
        print(e, flush=True)
        raise Exception("Database under maintenance", 500)

############################# validate user first name
USER_FIRST_NAME_MIN = 2
USER_FIRST_NAME_MAX = 20
REGEX_USER_FIRST_NAME = f"^.{{{USER_FIRST_NAME_MIN},{USER_FIRST_NAME_MAX}}}$"

def validate_user_first_name():
        user_first_name = request.form.get("user_first_name", "").strip()
        if not re.match(REGEX_USER_FIRST_NAME, user_first_name):
            raise Exception("company_exception user_first_name", 400)
        return user_first_name

############################# validate user last name
USER_LAST_NAME_MIN = 2
USER_LAST_NAME_MAX = 20
REGEX_USER_LAST_NAME = f"^.{{{USER_LAST_NAME_MIN},{USER_LAST_NAME_MAX}}}$"

def validate_user_last_name():
        user_last_name = request.form.get("user_last_name", "").strip()
        if not re.match(REGEX_USER_LAST_NAME, user_last_name):
            raise Exception("company_exception user_last_name", 400)
        return user_last_name

############################# validate user email
USER_EMAIL_MIN = 2
USER_EMAIL_MAX = 100
REGEX_USER_EMAIL = rf"^(?=.{{{USER_EMAIL_MIN},{USER_EMAIL_MAX}}}$)[^@]+@[^@]+\.[^@]+$"

def validate_user_email():
        user_email = request.form.get("user_email", "").strip()
        if not re.match(REGEX_USER_EMAIL, user_email):
            raise Exception("company_exception user_email", 400)
        return user_email

############################# validate user password
USER_PASSWORD_MIN = 8
USER_PASSWORD_MAX = 255
REGEX_USER_PASSWORD = f"^.{{{USER_PASSWORD_MIN},{USER_PASSWORD_MAX}}}$"

def validate_user_password():
        repeat_user_password = request.form.get("repeat_user_password", "")
        user_password = request.form.get("user_password", "")

        if not re.match(REGEX_USER_PASSWORD, user_password):
            raise Exception("company_exception user_password", 400)
        if user_password != repeat_user_password:
            raise Exception("company_exception password_mismatch", 400)
        return user_password


def validate_login_password():
        user_password = request.form.get("user_password", "")
        if not re.match(REGEX_USER_PASSWORD, user_password):
            raise Exception("company_exception user_password", 400)
        return user_password

############################# validate user phone
USER_PHONE_MIN = 2
USER_PHONE_MAX = 20
REGEX_USER_PHONE = rf"^(?=.{{{USER_PHONE_MIN},{USER_PHONE_MAX}}}$)[\d\s\+\-\(\)]+$"

def validate_user_phone():
        user_phone = request.form.get("user_phone", "").strip()
        if user_phone and not re.match(REGEX_USER_PHONE, user_phone):
            raise Exception("company_exception user_phone", 400)
        return user_phone

############################# validate user adress
USER_ADDRESS_MIN = 2
USER_ADDRESS_MAX = 150
REGEX_USER_ADDRESS = rf"^(?=.{{{USER_ADDRESS_MIN},{USER_ADDRESS_MAX}}}$)[\w\s\.\,\-\#]+$"

def validate_user_address():
        user_address = request.form.get("user_address", "").strip()
        if user_address and not re.match(REGEX_USER_ADDRESS, user_address):
            raise Exception("company_exception user_address", 400)
        return user_address

############################# validate user website
USER_WEBSITE_MIN = 2
USER_WEBSITE_MAX = 150
REGEX_USER_WEBSITE = rf"^(?=.{{{USER_WEBSITE_MIN},{USER_WEBSITE_MAX}}}$)(https?://)?(www\.)?[\w\-]+\.[a-z]{{2,}}.*$"

def validate_user_website():
        user_website = request.form.get("user_website", "").strip()
        if user_website and not re.match(REGEX_USER_WEBSITE, user_website):
            raise Exception("company_exception user_website", 400)
        return user_website


#############################
def no_cache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view

