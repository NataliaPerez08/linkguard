from flask import Flask, redirect, url_for, request, session, jsonify
from flask_session import Session
# Python standard libraries
import json
import os
import sqlite3

# Third-party libraries
from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from linkguard.orquestador.db import init_db_command,init_app
from linkguard.orquestador.user import User
from linkguard.orquestador.privateNetwork import PrivateNetwork
from linkguard.orquestador.endpoint import Endpoint


from dotenv import load_dotenv

load_dotenv()
# Configuración de la aplicación

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY", "your_default_secret_key") # Asegúrate de usar una clave secreta
app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'linkguard'
app.config['SESSION_FILE_THRESHOLD'] = 100
app.config['SESSION_FILE_MODE'] = 384
app.config['SESSION_FILE_DIR'] = '/tmp'
app.config['SESSION_FILE_CLEANUP_TIMEOUT'] = 86400
app.config['SESSION_FILE_DIR'] = '/tmp'

Session(app)

# Configuración de la base de datos
app.config['DATABASE'] = os.path.join(os.getcwd(), 'linkguard/orquestador/sqlite_db')
app.cli.add_command(init_db_command)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

try:
    init_db_command()
except Exception as e:
    print(e)


# OAuth 2 client setup
client = WebApplicationClient(os.getenv('GOOGLE_CLIENT_ID'))

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/")
def index():
    if current_user.is_authenticated:
        # Get the session cookie
        session_cookie = request.cookies.get(app.config['SESSION_COOKIE_NAME'])
        return {"logged_in": True, "session_cookie": session_cookie}
    else:
        return redirect(url_for("login"))
    
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# Login con Google
@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return {"url": request_uri}

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    
    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email)

    login_user(user)
    # Send user back to homepage
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register_simple", methods=["POST"])
def register_simple():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if User.create(name, email, password):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})
    
@app.route("/login_simple", methods=["POST"])
def login_simple():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = User.get(email)
    if user and user.check_password(password):
        login_user(user)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})
    
@app.route("/whoami")
def whoami():
    if current_user.is_authenticated:
        return jsonify({"user": current_user.name})
    else:
        return jsonify({"user": None})
    
@app.route("/get_virtual_private_networks")
@login_required
def get_virtual_private_networks():
    id_user = current_user.get_id()
    vpn = PrivateNetwork.get(id_user)
    return jsonify({'vpn': vpn})

@app.route("/create_virtual_private_network", methods=["POST"])
# crear_red_privada <nombre>"
@login_required
def create_virtual_private_network():
    data = request.get_json()
    name = data.get("name")
    id_user = current_user.get_id()
    default_mask = "24"
    default_ip = "10.0.0.0"
    vpn_id = PrivateNetwork.create(id_user, name, default_mask, default_ip)
    print(vpn_id)
    if vpn_id:
        return jsonify({"success": True, "name": name, "user_id": id_user, "vpn_id": vpn_id})
    else:
        return jsonify({"success": False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('./linkguard/orquestador/certs/server.crt', './linkguard/orquestador/certs/server.key'))