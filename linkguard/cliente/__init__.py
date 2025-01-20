import requests
import os
server = "https://127.0.0.1:443"

# Crea un servidor sobre el puerto 6443
from flask import Flask, jsonify, request, redirect, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config["SESSION_COOKIE_NAME"] = "google-login-session"

google_login_session = None

@app.route("/login")
def login_google():
    response = requests.get(server + "/login", verify=False)
    print("Go to the following URL and copy the cookies", response.content)
    cookies = str(input("Copy the session cookie and press enter"))
    google_login_session = {"google-login-session":cookies}
    return google_login_session

@app.route("/logout")
def logout():
    response = requests.get(server + "/logout", verify=False, cookies=google_login_session)
    print(response.content)


if __name__ == "__main__":
    app.run(port=6443)
