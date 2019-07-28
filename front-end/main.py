from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("Login.html")

@app.route("/info")
def info():
    return flask.jsonify({"info":"hello world"}),200

@app.route("/Welcome.html")
def about():
    return render_template("Welcome.html")

@app.route("/customer.html")
def customer():
    return render_template("customer.html")

@app.route("/serviceProvider.html")
def serviceProvider():
    return render_template("serviceProvider.html")

@app.route("/existingUser.html")
def existingUser():
    return render_template("existingUser.html")

@app.route("/ServicesList.html")
def serviceEvents():
    return render_template("ServicesList.html")

@app.route("/BidEvent.html", methods=['GET'])
def bid_event():
	print(request.args.get('event'))
	return render_template("BidEvent.html", event = request.args.get('event'))

if __name__ == "__main__":
    app.run()