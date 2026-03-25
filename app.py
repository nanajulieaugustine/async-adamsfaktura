from flask import Flask, render_template, request, jsonify, session, redirect
import x
from flask_cors import CORS
import uuid
import time
import os
from flask_session import Session
 
from icecream import ic
ic.configureOutput(prefix=f'________ | ', includeContext=True)
 
app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")

app_env = os.getenv("APP_ENV", "development").lower()
is_production = app_env == "production"

default_cors_origins = "https://adamsfakturaapp.vercel.app"
cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", default_cors_origins).split(",")
    if origin.strip()
]

CORS(
    app,
    origins=cors_origins,
    supports_credentials=True
)
 
app.config['SESSION_TYPE'] = 'filesystem'
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = os.getenv(
    "SESSION_COOKIE_SAMESITE",
    "None" if is_production else "Lax"
)
app.config["SESSION_COOKIE_SECURE"] = os.getenv(
    "SESSION_COOKIE_SECURE",
    "true" if is_production else "false"
).lower() == "true"
Session(app)


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


################################        CREATE USER             ############################

#check user email is allowed
@app.post("/api-check-user-email")
def check_user_email():
    try:
        user_email = x.validate_user_email()
        db, cursor = x.db()
        q = "SELECT * FROM users WHERE user_email = %s"
        cursor.execute(q, (user_email, ))
        row = cursor.fetchone()
        if not row:
            return "Email ok", 200

        return "Email already in use", 400
    except Exception as ex:
        ic(ex)
        if "company_exception user_email" in str(ex):
            return "Invalid email adress", 400
        return "Error in system", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


#commit to database with validation
@app.post("/api-create-user")
def api_create_user():
    try:
        user_pk = uuid.uuid4().hex
        user_first_name = x.validate_user_first_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()
        user_address = x.validate_user_address()
        user_phone = x.validate_user_phone()
        user_website = x.validate_user_website()
        user_role = request.form.get("user_role", "user").strip()
        user_password = x.validate_user_password()
        user_created_at = ic(int(time.time()))

        db, cursor = x.db()
        q = "INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(q, (user_pk, user_first_name, user_last_name, user_email, user_address, user_phone, user_website, user_password, user_role, user_created_at))
        db.commit()
        return "ok"

    except Exception as ex:
        ic(ex)

        if "company_exception user_first_name" in str(ex):
            error_message = f"First name must be {x.USER_FIRST_NAME_MIN} to {x.USER_FIRST_NAME_MAX} characters"

            return f"""
            <browser mix-update="#span_first_name">{error_message}</browser>
            """, 400
        
        if "company_exception user_last_name" in str(ex):
            error_message = f"Last name must be {x.USER_LAST_NAME_MIN} to {x.USER_LAST_NAME_MAX} characters"

            return f"""
            <browser mix-update="#span_last_name">{error_message}</browser>
            """, 400
        
        if "company_exception user_email" in str(ex):
            error_message = f"Invalid e-mail adress"

            return f"""
            <browser mix-update="#span_email">{error_message}</browser>
            """, 400
        
        if "company_exception user_website" in str(ex):
            error_message = f"Invalid website URL"

            return f"""
            <browser mix-update="#span_website">{error_message}</browser>
            """, 400
        
        if "company_exception user_password" in str(ex):
            error_message = f"Password must be {x.USER_PASSWORD_MIN} to {x.USER_PASSWORD_MAX} characters"

            return f"""
            <browser mix-update="#span_password">{error_message}</browser>
            """, 400

        if "company_exception repeat_user_password" in str(ex):
            error_message = f"Password must be {x.USER_PASSWORD_MIN} to {x.USER_PASSWORD_MAX} characters"

            return f"""
            <browser mix-update="#span_repeat_password">{error_message}</browser>
            """, 400

        if "company_exception password_mismatch" in str(ex):
            return """
            <browser mix-update="#span_repeat_password">Passwords do not match</browser>
            """, 400

        if "Duplicate entry" in str(ex) and "user_email" in str(ex):
            return """
            <browser mix-update="#span_email">Email already in use</browser>
            """, 400
        
        if "company_exception user_website" in str(ex):
            error_message = f"Invalid website URL"
            return f"""
            <browser mix-update="#span_website">{error_message}</browser>
                """, 400

        if "company_exception user_website" in str(ex):
            error_message = f"Invalid website URL"
            return f"""
            <browser mix-update="#span_website">{error_message}</browser>
            """, 400
        
        if "company_exception user_phone" in str(ex):
            error_message = f"Invalid phone number"

            return f"""
            <browser mix-update="#span_phone">{error_message}</browser>
            """, 400
        
        if "company_exception user_address" in str(ex):
            error_message = f"Invalid address"

            return f"""
            <browser mix-update="#span_address">{error_message}</browser>
            """, 400

        ___tip = render_template("___tip.html", status="error",  message="Something went wrong signing up, please try again")
        return f"""<browser mix-after-begin="#tooltip">{___tip}</browser>""", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


################################        USER LOG IN             ############################

#login user
@app.post("/api-login-user")
def user_login():
    try:
        user_email = x.validate_user_email()
        user_password = x.validate_login_password()

        db, cursor = x.db()

        q = "SELECT * FROM users WHERE user_email = %s AND user_password = %s"
        cursor.execute(q, (user_email, user_password))
        user = cursor.fetchone()
        if not user:
            raise Exception("company_exception wrong e-mail or password", 400)
        
        session["user"] = user
        return "user logged in"

    except Exception as ex:
        ic(ex)

        if "company_exception wrong e-mail or password" in str(ex) or "company_exception user_email" in str(ex) or "company_exception user_password" in str(ex):
            return "Wrong e-mail or password", 400
        
        return "Something went wrong logging in, please try again", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


######################################### user profile ####################################

# show user profile template
@app.get("/profile")
@x.no_cache 
def profile():
    try:
        user = session.get("user", "")
        if not user: return redirect("/login?name=A")
        ic(user)
        return render_template("page_profile.html", user=user)
    except Exception as ex:
        ic(ex)
        return "error"

#logout user
@app.get("/logout")
def logout():
    try:
        session.clear()
        return redirect("/login")
    except Exception as ex:
        ic(ex)
        return "system under maintainence...", 500
