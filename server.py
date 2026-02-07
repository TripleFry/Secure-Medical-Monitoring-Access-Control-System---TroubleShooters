from flask import Flask, request, jsonify, render_template
from event_engine import EventEngine

app = Flask(__name__)
engine = EventEngine()

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(engine.state)

@app.route("/event", methods=["POST"])
def receive_event():
    data = request.json
    event_type = data.get("event")

    state = engine.process_event(event_type)
    return jsonify(state)

if __name__ == "__main__":
    app.run(debug=True)
