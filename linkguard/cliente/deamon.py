from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello Flask!"

if __name__ == "__main__":
    # Specify the host and port
    app.run(host="127.0.0.1", port=3048)