import firebase_admin
from firebase_admin import db
import flask
from flask_cors import CORS
from flask_mail import Mail, Message
import os
import requests
try:
    from google.appengine.api import urlfetch
    from requests_toolbelt.adapters import appengine
    appengine.monkeypatch()
except ImportError:
    pass

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "eventeasy-238107-firebase-adminsdk-o8h7f-f11a8396b9.json"

app = flask.Flask(__name__)
CORS(app)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'eventeasy546@gmail.com',
    "MAIL_PASSWORD": 'eventeasycse546'
}

app.config.update(mail_settings)
mail = Mail(app)

firebase_admin.initialize_app(options={
    "databaseURL": "https://eventeasy-238107.firebaseio.com"
})
EVENTS = db.reference("event")
USERS_CUSTOMER = db.reference("users/customer")
USERS_SP = db.reference("users/serviceprovider")

@app.route("/info")
def info():
    return flask.jsonify({"info":"hello world"}),200

@app.route("/listCustomer", methods=["GET"])
def get_customerlist():
    users = USERS_CUSTOMER.get()
    return flask.jsonify(users), 200

@app.route("/listServiceProvider", methods=["GET"])
def get_SPlist():
    users = USERS_SP.get()
    return flask.jsonify(users), 200

@app.route("/userCustomer", methods=["POST"])
def create_users_customer():
    request = flask.request.json
    created_user = USERS_CUSTOMER.push(request)
    return flask.jsonify({"user_id": created_user.key}), 200

@app.route("/userServiceProvider", methods=["POST"])
def create_users_SP():
    request = flask.request.json
    created_user = USERS_SP.push(request)
    return flask.jsonify({"user_id": created_user.key}), 200

@app.route("/event", methods=["POST"])
def create_event():
    request = flask.request.json
    place_id = request["location"]["place_id"]
    eventName = request["Name"]
    userMailID = request["emailId"]
    created_event = EVENTS.push(request)
    alertUserMail(eventName,userMailID)
    alertServiceProviders(place_id)
    return flask.jsonify({"event_id": created_event.key}), 201


@app.route("/event/<event_id>")
def get_event(event_id):
    event = _build_event(event_id)
    if not event:
        return flask.jsonify({"status": "object not found"}), 404
    return flask.jsonify(event), 200


@app.route("/event/<event_id>", methods=["PUT"])
def update_event(event_id):
    event = _build_event(event_id)
    if not event:
        return flask.jsonify({"status": "object not found"}), 404
    req = flask.request.json
    EVENTS.child(event_id).update(req)
    userMailID = req["emailId"]
    alertUpdateMail(userMailID)
    return flask.jsonify({"success": True}), 200


@app.route("/event/<event_id>", methods=["DELETE"])
def delete_hero(event_id):
    event = _build_event(event_id)
    if not event:
        return flask.jsonify({"status": "object not found"}), 404
    EVENTS.child(event_id).delete()
    return flask.jsonify({"success": True}), 200


@app.route("/event", methods=["GET"])
def list_events():
    events = EVENTS.get()
    return flask.jsonify(events), 200

def getSPList():
    users = USERS_SP.get()
    return users

def alertUserMail(eventname, mailId):
    with app.app_context():
        msg = Message(subject=eventname + " is created",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[mailId], # replace with your email for testing
                      body="Your event has been created. We will let you now if there are any updates or new bids!!")
        mail.send(msg)

def alertUpdateMail(mailId):
    with app.app_context():
        msg = Message(subject="Bid Value for your event has been updated",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[mailId], # replace with your email for testing
                      body="Yay!! You have a better bid for your event!! Log in to Event Easy to check the updated bids!")
        mail.send(msg)

def findServiceProviders(place_id):
    serviceProviders = getSPList()
    #print(serviceProviders)
    mailids = []
    for key in serviceProviders:
        locations = serviceProviders[key]["location"]
        print(locations)
        for location in locations:
            if location["place_id"] == place_id:
                mailids.append(serviceProviders[key]["emailId"])
    #print(mailids)
    return mailids


def send_mail_sp(mailids):
     with app.app_context():
        msg = Message(subject="Event Easy - Your service is required!",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=mailids, # replace with your email for testing
                      body="A new event has been created near a place you can provide service. Log in to event easy and bid away!!!")
        mail.send(msg)

def alertServiceProviders(place_id):
    mailids = findServiceProviders(place_id)
    if len(mailids) != 0:
        send_mail_sp(mailids)
    
def _build_event(event_id):
    event = EVENTS.child(event_id).get()
    if not event:
        return None
    return event


if __name__ == "__main__":
    app.run()

# unbind address using following code :
# $ lsof -i tcp:5000
# $ kill -9 <PID>