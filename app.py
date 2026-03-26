from flask import Flask, render_template, request, jsonify, session, redirect
from flask_cors import CORS
import x
import uuid
import time
from flask_session import Session

from icecream import ic
ic.configureOutput(prefix=f'----- | ', includeContext=True)
 
app = Flask(__name__)
# CORS(app, origins=["http://localhost:3000"])

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

#INIT
@app.get("/")
def index():
    return render_template("index.html")

#SHOW ALL USERS
@app.get("/users")
def get_users():
    try:
        db, cursor = x.db()
        q = "SELECT * FROM users"
        cursor.execute(q)
        users = cursor.fetchall()
        return jsonify(users)
    except Exception as ex:
        ic(ex)
        return "system under maintenance...", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



################################        CREATE USER             ############################

#commit to database with validation
@app.route("/createuser", methods=["POST"])
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
        user_created_at = int(time.time())

        db, cursor = x.db()
        q = "INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(q, (user_pk, user_first_name, user_last_name, user_email, user_address, user_phone, user_website, user_password, user_role, user_created_at))
        db.commit()
        return "User created successfully"

    except Exception as ex:
        print("ERROR:", ex)

        if "company_exception user_first_name" in str(ex):
            return f"First name must be {x.USER_FIRST_NAME_MIN} to {x.USER_FIRST_NAME_MAX} characters", 400
        
        if "company_exception user_last_name" in str(ex):
            return f"Last name must be {x.USER_LAST_NAME_MIN} to {x.USER_LAST_NAME_MAX} characters", 400
        
        if "company_exception user_email" in str(ex):
            return "Invalid e-mail address", 400
        
        if "company_exception user_password" in str(ex):
            return f"Password must be {x.USER_PASSWORD_MIN} to {x.USER_PASSWORD_MAX} characters", 400

        if "company_exception repeat_user_password" in str(ex):
            return f"Password must be {x.USER_PASSWORD_MIN} to {x.USER_PASSWORD_MAX} characters", 400

        if "company_exception password_mismatch" in str(ex):
            return "Passwords do not match", 400

        if "Duplicate entry" in str(ex) and "user_email" in str(ex):
            return "Email already in use", 400
        
        if "company_exception user_website" in str(ex):
            return "Invalid website URL", 400

        if "Duplicate entry" in str(ex) and "user_phone" in str(ex):
            return "Phone number already in use", 400
                
        if "company_exception user_phone" in str(ex):
            return "Invalid phone number", 400
        
        if "company_exception user_address" in str(ex):
            return "Invalid address", 400

        return "system under maintainence...", 500, {"Content-Type": "text/html"}
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


# ################################        USER LOG IN             ############################

# #login user
# @app.post("/api-login-user")
# def user_login():
#     try:
#         user_email = x.validate_user_email()
#         user_password = x.validate_login_password()

#         db, cursor = x.db()

#         q = "SELECT * FROM users WHERE user_email = %s AND user_password = %s"
#         cursor.execute(q, (user_email, user_password))
#         user = cursor.fetchone()
#         if not user:
#             raise Exception("company_exception wrong e-mail or password", 400)
        
#         session["user"] = user
#         return "user logged in"

#     except Exception as ex:
#         ic(ex)

#         if "company_exception wrong e-mail or password" in str(ex) or "company_exception user_email" in str(ex) or "company_exception user_password" in str(ex):
#             return "Wrong e-mail or password", 400
        
#         return "Something went wrong logging in, please try again", 500
    
#     finally:
#         if "cursor" in locals(): cursor.close()
#         if "db" in locals(): db.close()


# ######################################### user profile ####################################

# # show user profile template
# @app.get("/profile")
# @x.no_cache 
# def profile():
#     try:
#         user = session.get("user", "")
#         if not user: return redirect("/login?name=A")
#         ic(user)
#         return render_template("page_profile.html", user=user)
#     except Exception as ex:
#         ic(ex)
#         return "error"

# #logout user
# @app.get("/logout")
# def logout():
#     try:
#         session.clear()
#         return redirect("/login")
#     except Exception as ex:
#         ic(ex)
#         return "system under maintainence...", 500


# @app.get("/api-show-users")
# def showusers():
#     try:
#         db, cursor = x.db()
#         q = "SELECT * FROM users"
#         cursor.execute(q)
#         users = cursor.fetchall()
#         return jsonify(users)
#     except Exception as ex:

#         ic(ex)
#         return "system under maintenance...", 500
    
#     finally:
#         if "cursor" in locals(): cursor.close()
#         if "db" in locals(): db.close()