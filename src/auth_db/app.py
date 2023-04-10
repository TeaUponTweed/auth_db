import logging
import os
import uuid
from datetime import timedelta
from typing import Optional

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
)
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from auth_db.db import (
    User,
    check_token,
    get_user_id,
    make_new_user,
    reset_pw,
    update_password,
    validate_user,
)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "change-this-please-39238493"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "change-this-as-well-23498723"
jwt = JWTManager(app)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


@app.route("/")
def home():
    return send_file("static/index.html")


def login(email: str, password: Optional[str], pw: str):
    if password is None:
        print(f"Null {email} password")
        return jsonify({"msg": "Login Failed"}), 401

    if pw is None:
        pw = validate_user(email)

    if pw is None:
        print(f"Unknown email {email}")
        return jsonify({"msg": "Login Failed"}), 401

    if not check_password_hash(pw, password):
        print(f"Failed {email} password check")
        return jsonify({"msg": "Login Failed"}), 401

    access_token = create_access_token(identity=email)
    return jsonify(access_token=access_token)


@app.route("/signup", methods=["POST"])
def signup():
    email = request.json.get("email", None)
    if email is None:
        return jsonify({"msg": "No email provided"}), 401

    pw = request.json.get("password", None)
    if pw is None:
        return jsonify({"msg": "No password provided"}), 401

    already_exists_pw = validate_user(email)
    if already_exists_pw is not None:
        return login(email, pw, already_exists_pw)

    hashed_pw = generate_password_hash(pw)
    user = User(
        email=email,
        password=hashed_pw,
    )
    make_new_user(user)
    return login(email, pw, None)


@app.route("/auth", methods=["GET"])
@jwt_required()
def check_auth():
    return jsonify({}), 200


@app.route("/try_reset_password", methods=["POST"])
def try_reset_password():
    email = request.json.get("email", None)
    if email is None:
        return jsonify({"msg": "No email provided"}), 401
    token = reset_pw(email=email)
    if token is not None:
        # send email with link
        email_html = f"""
        <body>
          <p>
             Hello, <br />
             Please go <a href="http://0.0.0.0:8080/reset_password?token={token}">here</a> to reset your password.
          </p>
       </body>
        """
        print(email_html)

    return jsonify({}), 200


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        token = request.args.get("token")
        return render_template("reset_password.html", token=token)
    elif request.method == "POST":
        token = request.form["token"]
        pw = request.form["password"]
        user = check_token(token=token)
        if user:
            pw = generate_password_hash(pw)
            update_password(email=user.email, pw=pw)
            return redirect("/static/login.html")
        else:
            return 'Token not recognized! Try to <a href="/static/forgot_password.html">reset</a> again.'


@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)
