# # device/mockHa.py
# from flask import Flask, jsonify, request

# app = Flask(__name__)

# states = {
#     "light.living_room": {"state": "off", "brightness": 0},
#     "switch.heater": {"state": "off"},
#     "sensor.temperature": {"state": "22.5", "unit": "°C"}
# }

# @app.route('/api/states/<entityId>', methods=['GET'])
# def get_state(entityId):
#     if entityId in states:
#         return jsonify(states[entityId])
#     return jsonify({"error": "Not found"}), 404

# @app.route('/api/states/<entityId>', methods=['POST'])
# def update_state(entityId):
#     data = request.get_json()
#     if entityId in states:
#         states[entityId].update(data)
#         return jsonify({"result": "ok", "new_state": states[entityId]})
#     return jsonify({"error": "Entity not found"}), 404

# @app.route('/api/services/<domain>/<service>', methods=['POST'])
# def call_service(domain, service):
#     data = request.get_json()
#     entityId = data.get("entity_id")
#     if entityId in states:
#         if "turn_on" in service:
#             states[entityId]["state"] = "on"
#         elif "turn_off" in service:
#             states[entityId]["state"] = "off"
#         return jsonify({"result": "ok", "new_state": states[entityId]})
#     return jsonify({"error": "Entity not found"}), 404

# if __name__ == '__main__':
#     app.run(port=8123)


# device/mockHa.py
from flask import Flask, jsonify, request

app = Flask(__name__)

# ---------------------------
# Simulated home device status database
# ---------------------------
states = {
    # light
    "light.living_room": {"state": "off", "brightness": 0},
    "light.dining_room": {"state": "off", "brightness": 0},
    "light.kitchen": {"state": "off", "brightness": 0},
    "light.bathroom": {"state": "off", "brightness": 0},
    "light.bedroom": {"state": "off", "brightness": 0},

    # aircon
    "ac.living_room": {"state": "off", "temperature": 24},
    "ac.dining_room": {"state": "off", "temperature": 24},
    "ac.kitchen": {"state": "off", "temperature": 24},
    "ac.bathroom": {"state": "off", "temperature": 24},
    "ac.bedroom": {"state": "off", "temperature": 24},

    # curtain
    "curtain.living_room": {"state": "closed"},
    "curtain.dining_room": {"state": "closed"},
    "curtain.kitchen": {"state": "closed"},
    "curtain.bathroom": {"state": "closed"},
    "curtain.bedroom": {"state": "closed"},

    # tv）
    "tv.living_room": {"state": "off", "volume": 20},

    # temperature sensor
    "sensor.temperature": {"state": "22.5", "unit": "°C"}
}


# ---------------------------
# Get device status
# ---------------------------
@app.route('/api/states/<entityId>', methods=['GET'])
def get_state(entityId):
    if entityId in states:
        return jsonify(states[entityId])
    return jsonify({"error": "Not found"}), 404


# ---------------------------
# Update device status (general POST)
# ---------------------------
@app.route('/api/states/<entityId>', methods=['POST'])
def update_state(entityId):
    data = request.get_json()
    if entityId in states:
        states[entityId].update(data)
        return jsonify({"result": "ok", "new_state": states[entityId]})
    return jsonify({"error": "Entity not found"}), 404


# ---------------------------
# Call the service interface (simulating Home Assistant style)
# ---------------------------
@app.route('/api/services/<domain>/<service>', methods=['POST'])
def call_service(domain, service):
    data = request.get_json()
    entityId = data.get("entity_id")
    if entityId not in states:
        return jsonify({"error": "Entity not found"}), 404

    # light control
    if domain == "light":
        if "turn_on" in service:
            states[entityId]["state"] = "on"
            states[entityId]["brightness"] = 100
        elif "turn_off" in service:
            states[entityId]["state"] = "off"
            states[entityId]["brightness"] = 0

    # ac control
    elif domain == "ac":
        if "turn_on" in service:
            states[entityId]["state"] = "on"
        elif "turn_off" in service:
            states[entityId]["state"] = "off"
        elif "set_temperature" in service:
            # Allow setting the target temperature via JSON body
            new_temp = data.get("temperature")
            if new_temp is not None:
                states[entityId]["temperature"] = new_temp

    # curtain control
    elif domain == "curtain":
        if "open" in service:
            states[entityId]["state"] = "open"
        elif "close" in service:
            states[entityId]["state"] = "closed"

    # tv control
    elif domain == "tv":
        if "turn_on" in service:
            states[entityId]["state"] = "on"
        elif "turn_off" in service:
            states[entityId]["state"] = "off"
        elif "set_volume" in service:
            new_volume = data.get("volume")
            if new_volume is not None:
                states[entityId]["volume"] = new_volume

    else:
        return jsonify({"error": f"Unsupported domain: {domain}"}), 400

    return jsonify({"result": "ok", "new_state": states[entityId]})


# ---------------------------
# Start the simulation server
# ---------------------------
if __name__ == '__main__':
    app.run(port=8123)
