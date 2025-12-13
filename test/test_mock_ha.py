# test/test_mock_ha.py
import sys
import os
import json
import unittest

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the Flask app — this will initialize `states`
from device.mockHa import app, states


class TestMockHomeAssistant(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        # Reset states to known initial state before each test
        self.initial_states = {
            "light.living_room": {"state": "off", "brightness": 0},
            "light.bedroom": {"state": "off", "brightness": 0},
            "ac.bedroom": {"state": "off", "temperature": 24},
            "curtain.living_room": {"state": "closed"},
            "tv.living_room": {"state": "off", "volume": 20},
            "sensor.temperature": {"state": "22.5", "unit": "°C"}
        }
        # Deep copy initial state
        for k, v in self.initial_states.items():
            states[k] = v.copy()

    def test_get_state_existing_entity(self):
        response = self.client.get('/api/states/light.living_room')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, {"state": "off", "brightness": 0})

    def test_get_state_nonexistent_entity(self):
        response = self.client.get('/api/states/non.existent')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_update_state_existing_entity(self):
        payload = {"state": "on", "brightness": 80}
        response = self.client.post(
            '/api/states/light.living_room',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["new_state"]["state"], "on")
        self.assertEqual(data["new_state"]["brightness"], 80)

        # Verify global state updated
        self.assertEqual(states["light.living_room"]["state"], "on")

    def test_update_state_nonexistent_entity(self):
        response = self.client.post(
            '/api/states/non.existent',
            data=json.dumps({"state": "on"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

    def test_light_turn_on(self):
        response = self.client.post(
            '/api/services/light/turn_on',
            data=json.dumps({"entity_id": "light.bedroom"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["new_state"]["state"], "on")
        self.assertEqual(data["new_state"]["brightness"], 100)

    def test_light_turn_off(self):
        # First turn on
        states["light.bedroom"] = {"state": "on", "brightness": 100}
        response = self.client.post(
            '/api/services/light/turn_off',
            data=json.dumps({"entity_id": "light.bedroom"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["new_state"]["state"], "off")
        self.assertEqual(data["new_state"]["brightness"], 0)

    def test_ac_turn_on_and_set_temperature(self):
        # Turn on
        response = self.client.post(
            '/api/services/ac/turn_on',
            data=json.dumps({"entity_id": "ac.bedroom"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(states["ac.bedroom"]["state"], "on")

        # Set temperature
        response = self.client.post(
            '/api/services/ac/set_temperature',
            data=json.dumps({"entity_id": "ac.bedroom", "temperature": 26}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(states["ac.bedroom"]["temperature"], 26)

    def test_curtain_open_close(self):
        response = self.client.post(
            '/api/services/curtain/open',
            data=json.dumps({"entity_id": "curtain.living_room"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(states["curtain.living_room"]["state"], "open")

        response = self.client.post(
            '/api/services/curtain/close',
            data=json.dumps({"entity_id": "curtain.living_room"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(states["curtain.living_room"]["state"], "closed")

    def test_tv_turn_on_and_set_volume(self):
        response = self.client.post(
            '/api/services/tv/turn_on',
            data=json.dumps({"entity_id": "tv.living_room"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(states["tv.living_room"]["state"], "on")

        response = self.client.post(
            '/api/services/tv/set_volume',
            data=json.dumps({"entity_id": "tv.living_room", "volume": 50}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(states["tv.living_room"]["volume"], 50)

    def test_unsupported_domain(self):
        # Use an EXISTING entity_id but an unsupported domain to trigger 400
        response = self.client.post(
            '/api/services/fan/turn_on',
            data=json.dumps({"entity_id": "light.living_room"}),  # ← exists!
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("Unsupported domain", data["error"])

    def test_service_nonexistent_entity(self):
        response = self.client.post(
            '/api/services/light/turn_on',
            data=json.dumps({"entity_id": "light.nonexistent"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)