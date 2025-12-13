# test_main.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add current directory to path to import main
sys.path.insert(0, os.path.dirname(__file__))

from main import SmartHomeSystem
from Classifier.task_classifier import Intent


class TestSmartHomeSystem(unittest.TestCase):

    def setUp(self):
        # Mock heavy dependencies during SmartHomeSystem initialization
        with patch('main.WhisperAsr'), \
             patch('main.LLMProxy') as mock_llm_proxy_class, \
             patch('main.DeviceController') as mock_device_ctrl_class:

            self.mock_llm_proxy = MagicMock()
            mock_llm_proxy_class.return_value = self.mock_llm_proxy

            self.mock_device_ctrl = MagicMock()
            mock_device_ctrl_class.return_value = self.mock_device_ctrl

            self.system = SmartHomeSystem()
            self.system.mode = "text"  # Force text mode for predictable testing

    # ———————— Entity Resolution Tests ————————
    def test_resolveEntityId_defaults_to_living_room_light(self):
        self.assertEqual(self.system.resolveEntityId("turn on the light"), "light.living_room")

    def test_resolveEntityId_handles_bedroom_light(self):
        self.assertEqual(self.system.resolveEntityId("bedroom light on"), "light.bedroom")
        self.assertEqual(self.system.resolveEntityId("打开卧室的灯"), "light.bedroom")

    def test_resolveEntityId_handles_kitchen_ac(self):
        self.assertEqual(self.system.resolveEntityId("turn on kitchen AC"), "ac.kitchen")
        self.assertEqual(self.system.resolveEntityId("厨房空调"), "ac.kitchen")

    def test_resolveEntityId_falls_back_to_light_if_no_device_found(self):
        self.assertEqual(self.system.resolveEntityId("play music in bathroom"), "light.bathroom")

    # ———————— Simple Intent Handling ————————
    def test_handleSimpleIntent_turn_on(self):
        self.mock_device_ctrl.executeCommand.return_value = "OK"
        result = self.system.handleSimpleIntent(Intent.TURN_ON, "turn on light")
        self.mock_device_ctrl.executeCommand.assert_called_with("light.living_room", "turn_on")
        self.assertEqual(result, "OK")

    def test_handleSimpleIntent_query_status(self):
        self.mock_device_ctrl.getDeviceStatus.return_value = "ON"
        result = self.system.handleSimpleIntent(Intent.QUERY_STATUS, "status of heater")
        self.mock_device_ctrl.getDeviceStatus.assert_called_with("switch.living_room")
        self.assertEqual(result, "ON")

    def test_handleSimpleIntent_unknown_intent(self):
        result = self.system.handleSimpleIntent("UNKNOWN", "some command")
        self.assertEqual(result, "Unknown intent")

    # ———————— Main Loop Behavior ————————
    @patch('builtins.input', side_effect=["voice", "quit"])
    @patch('builtins.print')
    def test_loopOnce_switches_to_voice_mode(self, mock_input, mock_print):
        self.system.mode = "text"
        result = self.system.loopOnce()  # processes "voice"
        self.assertTrue(result)
        self.assertEqual(self.system.mode, "voice")

    @patch('builtins.input', side_effect=["quit"])
    def test_loopOnce_exits_on_quit(self, mock_input):
        result = self.system.loopOnce()
        self.assertFalse(result)  # should signal exit

    @patch('builtins.input', side_effect=["exit"])
    def test_loopOnce_exits_on_exit(self, mock_input):
        result = self.system.loopOnce()
        self.assertFalse(result)

    @patch('builtins.input', side_effect=["turn on bedroom light", "quit"])
    @patch('builtins.print')
    def test_loopOnce_processes_simple_intent(self, mock_input, mock_print):
        with patch.object(self.system.classifier, 'classify', return_value=Intent.TURN_ON):
            self.system.loopOnce()
            self.mock_device_ctrl.executeCommand.assert_called_with("light.bedroom", "turn_on")

    @patch('builtins.input', side_effect=["What's my Wi-Fi password?", "quit"])
    @patch('builtins.print')
    def test_loopOnce_processes_complex_intent(self, mock_input, mock_print):
        with patch.object(self.system.classifier, 'classify', return_value=Intent.COMPLEX):
            self.system.loopOnce()
            self.mock_llm_proxy.handle_complex_query.assert_called_with("What's my Wi-Fi password?")


if __name__ == '__main__':
    unittest.main(verbosity=2)