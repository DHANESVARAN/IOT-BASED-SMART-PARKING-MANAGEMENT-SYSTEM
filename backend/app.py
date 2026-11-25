from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import pickle
import numpy as np

app = Flask(__name__)
CORS(app)

# Initialize the 20 Walmart slots
slots = {f"W-{i}": {"id": f"W-{i}", "status": "AVAILABLE"} for i in range(1, 21)}
event_log = []

# Try Loading Pre-trained Regressor Artifact
try:
    with open('backend/models/rf_parking_model.pkl', 'rb') as f:
        model = pickle.load(f)
        print("Pre-trained Random Forest loaded successfully.")
except FileNotFoundError:
    model = None
    print("Warning: Model missing. Run `train_model.py` to construct model artifacts.")

@app.route('/api/slots', methods=['GET'])
def get_slots():
    """Returns the current state of all parking slots."""
    return jsonify({"success": True, "data": list(slots.values())})

@app.route('/api/events/stream', methods=['GET'])
def get_event_stream():
    """Returns the latest events for the React UI."""
    return jsonify({"success": True, "data": event_log})

@app.route('/api/simulator/events', methods=['POST'])
def receive_event():
    """Receives virtual sensor events from the external simulator engine."""
    data = request.json
    slot_id = data.get('slot_id')
    state = data.get('state')

    if slot_id in slots:
        slots[slot_id]['status'] = state

        log_entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "slot": slot_id,
            "event": state
        }
        event_log.insert(0, log_entry)

        if len(event_log) > 50:
            event_log.pop()

        return jsonify({"success": True, "message": "Event processed"})

    return jsonify({"success": False, "error": "Invalid slot ID"}), 400

@app.route('/api/predictions/availability', methods=['GET'])
def get_predictive_forecast():
    """Calculates occupancy 60 minutes into the future using pre-trained model metadata."""
    if model is None:
         occupied_count = sum(1 for s in slots.values() if s['status'] == 'OCCUPIED')
         percent_busy = int((occupied_count / 20) * 100)
         return jsonify({"success": True, "forecasted_availability": percent_busy, "model": "Persistence Baseline"})

    now = datetime.now() + timedelta(hours=1)
    hour = now.hour
    is_weekend = 1 if now.weekday() >= 5 else 0
    occupied_lag_1 = sum(1 for s in slots.values() if s['status'] == 'OCCUPIED')

    features = np.array([[hour, is_weekend, occupied_lag_1]])
    predicted_occupancy = int(np.clip(model.predict(features)[0], 0, 20))
    percent_busy = int((predicted_occupancy / 20) * 100)

    return jsonify({
        "success": True,
        "forecasted_availability": percent_busy,
        "model": "RandomForestRegressor"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
