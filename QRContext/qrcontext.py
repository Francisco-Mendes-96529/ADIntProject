import os
import secrets
from urllib.parse import urlencode

from dotenv import load_dotenv
from flask import (
    Flask,
    redirect,
    url_for,
    render_template,
    flash,
    session,
    current_app,
    request,
    abort,
    send_from_directory,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import requests
import json

load_dotenv()

FILE_DIR = "./files/"

app = Flask(__name__)
# Enable CORS for all routes
# CORS(app)
app.config["SECRET_KEY"] = "top secret!"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["OAUTH2_PROVIDERS"] = {
    # Google OAuth 2.0 documentation:
    # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
    "fenix": {
        "client_id": os.environ.get("FENIX_CLIENT_ID"),
        "client_secret": os.environ.get("FENIX_CLIENT_SECRET"),
        "authorize_url": "https://fenix.tecnico.ulisboa.pt/oauth/userdialog",
        "token_url": "https://fenix.tecnico.ulisboa.pt/oauth/access_token",
        "userinfo": {
            "url": "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person",
            "email": lambda json: json["email"],
        },
        "scopes": [],
        # 'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
    },
}

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = "index"


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    token = db.Column(db.String(300))


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("index"))


@app.route("/authorize/<provider>")
def oauth2_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for("index"))

    provider_data = current_app.config["OAUTH2_PROVIDERS"].get(provider)
    if provider_data is None:
        abort(404)

    # generate a random string for the state parameter
    session["oauth2_state"] = secrets.token_urlsafe(16)

    # create a query string with all the OAuth2 parameters
    qs = urlencode(
        {
            "client_id": provider_data["client_id"],
            "redirect_uri": url_for(
                "oauth2_callback", provider=provider, _external=True
            ),
            "response_type": "code",
            "scope": " ".join(provider_data["scopes"]),
            "state": session["oauth2_state"],
        }
    )

    # redirect the user to the OAuth2 provider authorization URL
    return redirect(provider_data["authorize_url"] + "?" + qs)


@app.route("/callback/<provider>")
def oauth2_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for("index"))

    provider_data = current_app.config["OAUTH2_PROVIDERS"].get(provider)
    if provider_data is None:
        abort(404)

    # if there was an authentication error, flash the error messages and exit
    if "error" in request.args:
        for k, v in request.args.items():
            if k.startswith("error"):
                flash(f"{k}: {v}")
        return redirect(url_for("index"))

    # make sure that the state parameter matches the one we created in the
    # authorization request
    if request.args["state"] != session.get("oauth2_state"):
        abort(401)

    # make sure that the authorization code is present
    if "code" not in request.args:
        abort(401)

    # exchange the authorization code for an access token
    response = requests.post(
        provider_data["token_url"],
        data={
            "client_id": provider_data["client_id"],
            "client_secret": provider_data["client_secret"],
            "code": request.args["code"],
            "grant_type": "authorization_code",
            "redirect_uri": url_for(
                "oauth2_callback", provider=provider, _external=True
            ),
        },
        headers={"Accept": "application/json"},
    )
    if response.status_code != 200:
        abort(401)
    oauth2_token = response.json().get("access_token")
    print(oauth2_token)
    if not oauth2_token:
        abort(401)

    # use the access token to get the user's email address
    response = requests.get(
        provider_data["userinfo"]["url"],
        headers={
            "Authorization": "Bearer " + oauth2_token,
            "Accept": "application/json",
        },
    )
    if response.status_code != 200:
        abort(401)
    email = provider_data["userinfo"]["email"](response.json())

    # find or create the user in the database
    user = db.session.scalar(db.select(User).where(User.email == email))
    if user is None:
        user = User(email=email, username=email.split("@")[0], token=oauth2_token)
        db.session.add(user)
        db.session.commit()

    else:
        # Update the token field in any case
        user.token = oauth2_token

        # Commit the changes to the database
        db.session.commit()

    # log the user in
    login_user(user)
    return redirect(location="/#mainMenu")


@app.route("/files/html5-qrcode.min.js")
def readerjs():
    return send_from_directory(directory=FILE_DIR, path="html5-qrcode.min.js")


@app.route("/API/QRCodeReader/<path:data>")
def qrCodeReader(data):
    print("Data received:", data)

    try:
        if data.split("/")[0] == "menu":
            resId = data.split("/")[1]
            # Define the URL of the other server where you want to send the data via a GET request
            other_server_url = "http://127.0.0.1:5002/API/restaurant/" + resId

            # Send the "decodedText" to the other Flask server via a GET request
            response = requests.get(other_server_url)

        elif data.split("/")[0] == "spaces":
            # URL of the RoomService server
            room_server_url = "http://127.0.0.1:5003/API/" + data

            # Make a GET request to the API
            response = requests.get(room_server_url)

        else:
            return "Received wrong formated data", 400

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            # If the request to Server fails
            return f"Requests error: {response.text}", response.status_code

    except Exception as e:
        # Handle other exceptions
        return f"Error: {e}", 500


@app.route("/API/checkin/<userId>", methods=["POST", "GET"])
def checkin(userId):
    if request.method == "POST":
        # Make a POST request to the local API endpoint
        print(userId)
        data = {"roomId": request.json.get("roomId")}
        response = requests.post(
            "http://127.0.0.1:5004/API/checkin/" + userId, json=data
        )

        # You can also check the response from the API
        if response.status_code == 201:
            # Do something with the response data if needed
            return "Check-in successful", 201
        else:
            return response.text, response.status_code
    else:
        response = requests.get("http://127.0.0.1:5004/API/checkin/" + userId)
        return response.json(), response.status_code


@app.route("/API/checkout", methods=["POST"])
def checkout():
    # Make a POST request to the local API endpoint
    userId = current_user.username
    data = {"userId": userId}
    response = requests.post("http://127.0.0.1:5004/API/checkout", json=data)

    # You can also check the response from the API
    if response.status_code == 201:
        # Do something with the response data if needed
        return "Check-out successful", 201
    else:
        return response.text, response.status_code


@app.route("/API/<path:roomId>/users")
def usersCheckedin(roomId):
    try:
        response = requests.get("http://127.0.0.1:5004/API/" + roomId + "/users")

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            # If the request to Server fails
            return f"Requests error: {response.text}", response.status_code

    except Exception as e:
        # Handle other exceptions
        return f"Error: {e}", 500


@app.route("/API/messages", methods=["GET", "POST"])
def messages():
    try:
        url = "http://127.0.0.1:5005/API/messages/" + current_user.username
        if request.method == "GET":
            other_user = request.args.get("other_user")
            response = requests.get(url, data=other_user)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                # If the request to Server fails
                return f"Requests error: {response.text}", response.status_code

        else:
            # Send the POST request
            response = requests.post(url, json=request.json)

            # Check if the request was successful (status code 200)
            if response.status_code == 201:
                return jsonify(response.json())
            else:
                # If the request to Server fails
                return f"Requests error: {response.text}", response.status_code

    except Exception as e:
        # Handle other exceptions
        return f"Error: {e}", 500


@app.route("/API/evaluation", methods=["POST"])
def evaluation():
    try:
        resId = request.json.get("resId").split("/")[1]
        print(resId)
        data = {
            "resId": resId,
            "userId": request.json.get("userId"),
            "eval": request.json.get("eval"),
            "rating": request.json.get("rating"),
        }

        response = requests.post("http://127.0.0.1:5002/API/evaluation", json=data)
        return response.text, response.status_code
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/API/person/courses")
def getCourses():
    try:
        response = requests.get(
            "https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person/courses",
            headers={
                "Authorization": "Bearer " + current_user.token,
                "Accept": "application/json",
            },
        )
        if response.status_code != 200:
            abort(401, "not authorized")

        user_info = response.json()
        return jsonify(user_info)
    except:
        abort(401, "not logged in in FLASK")


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
