import time
import random
import requests
from datetime import datetime

API_URL = "http://localhost:5000/api/simulator/events"
SLOT_IDS = [f"W-{i}" for i in range(1, 21)]

def generate_event():
    # Constructing the simulated sensor payload[cite: 14]
    payload = {
        "event_id": f"SIM-{int(time.time())}",
        "slot_id": random.choice(SLOT_IDS),
        "timestamp": datetime.now().isoformat(),
        "state": random.choice(["OCCUPIED", "VACANT"]),
        "source": "SIMULATOR"
    }

    try:
        requests.post(API_URL, json=payload)
        print(f"[{payload['timestamp']}] Emitted {payload['state']} for {payload['slot_id']}")
    except Exception as e:
        print(f"Failed to transmit event: {e}")

if __name__ == "__main__":
    print("Walmart Local Simulator Engine Started...")
    while True:
        generate_event()
        # Random interval between 2 and 5 seconds for visual testing
        time.sleep(random.randint(2, 5))
