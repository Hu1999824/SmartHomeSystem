# task_classifier.py~
import re
from enum import Enum
from typing import Tuple, Optional

# === 直接在本文件里定义 SIMPLE_COMMANDS（移到顶部） ===
SIMPLE_COMMANDS = {
    ("turn on the light", "turn on the lights", "light on", "switch on the light", "enable light"): "light_on",
    ("turn off the light", "turn off the lights", "light off", "switch off the light", "disable light"): "light_off",

    # Air Conditioner
    ("turn on the air conditioner", "turn on ac", "ac on", "start cooling", "enable ac"): "ac_on",
    ("turn off the air conditioner", "turn off ac", "ac off", "disable ac"): "ac_off",
    ("increase temperature", "temperature up", "make it warmer", "raise temperature"): "ac_temp_up",
    ("decrease temperature", "temperature down", "make it cooler", "lower temperature"): "ac_temp_down",
    ("set temperature to", "set ac temperature to", "set air conditioner to"): "ac_set_temp",

    # Curtain
    ("open curtain", "draw curtain", "open the curtain", "raise curtain"): "curtain_open",
    ("close curtain", "shut curtain", "close the curtain", "lower curtain"): "curtain_close",

    # TV
    ("turn on the tv", "tv on", "switch on the tv", "enable tv", "open tv"): "tv_on",
    ("turn off the tv", "tv off", "switch off the tv", "disable tv", "close tv"): "tv_off",
    ("increase volume", "volume up", "make tv louder"): "tv_volume_up",
    ("decrease volume", "volume down", "make tv quieter"): "tv_volume_down",

    # Heater
    ("turn on heater", "heater on", "enable heater", "start heating"): "heater_on",
    ("turn off heater", "heater off", "disable heater", "stop heating"): "heater_off",

    ("play music", "start music", "resume music"): "play_music",
    ("pause music", "stop music"): "pause_music",
    ("next track", "skip song"): "next_track",
    ("volume up", "louder", "increase volume"): "volume_up",
    ("volume down", "quieter", "decrease volume"): "volume_down",

    ("turn on fan", "fan on"): "fan_on",
    ("turn off fan", "fan off"): "fan_off",

    ("reboot", "restart system"): "reboot",
    ("shut down", "power off"): "shutdown",
}

# ======== Intent enum ========
class Intent(Enum):
    TURN_ON = "turn_on"
    TURN_OFF = "turn_off"
    QUERY_STATUS = "query_status"
    COMPLEX = "complex"

# ======== Compile all command modes ========
COMPILED_PATTERNS = []
for phrases, action in SIMPLE_COMMANDS.items():
    escaped = [re.escape(p.lower()) for p in phrases]
    pattern = "|".join(escaped)
    COMPILED_PATTERNS.append((re.compile(r"\b(" + pattern + r")\b"), action))

# ======== Mapping simple task actions to intentions ========
ACTION_TO_INTENT = {
    "light_on": Intent.TURN_ON,
    "light_off": Intent.TURN_OFF,
    "tv_on": Intent.TURN_ON,
    "tv_off": Intent.TURN_OFF,
    "ac_on": Intent.TURN_ON,
    "ac_off": Intent.TURN_OFF,
    "curtain_open": Intent.TURN_ON,
    "curtain_close": Intent.TURN_OFF,
    "fan_on": Intent.TURN_ON,
    "fan_off": Intent.TURN_OFF,
    "play_music": Intent.TURN_ON,
    "pause_music": Intent.TURN_OFF,
    "next_track": Intent.TURN_ON,
    "volume_up": Intent.TURN_ON,
    "volume_down": Intent.TURN_OFF,
    "reboot": Intent.COMPLEX,   # System-level commands are processed by the LLM.
    "shutdown": Intent.COMPLEX,
}

class TaskClassifier:
    def __init__(self):
        self.patterns = COMPILED_PATTERNS

    def classify(self, text: str) -> Intent:
        if not text or not text.strip():
            return Intent.COMPLEX

        text_lower = text.strip().lower()

        # Too long → Complex
        if len(text_lower) > 60:
            return Intent.COMPLEX

        # complex_indicators
        complex_indicators = [
            "how", "why", "what is", "explain", "summarize", "write", "generate",
            "can you", "could you", "help me", "tell me", "?", "please"
        ]
        if any(ind in text_lower for ind in complex_indicators):
            return Intent.COMPLEX

        # Simple command matching
        for pattern, action in self.patterns:
            if pattern.search(text_lower):
                return ACTION_TO_INTENT.get(action, Intent.COMPLEX)

        return Intent.COMPLEX

    def record_feedback(self, text: str, predicted: Intent, corrected: Intent):
        print(f"[反馈学习] '{text}' 预测={predicted.value} → 修正={corrected.value}")


def is_simple_task(text: str) -> Tuple[bool, Optional[str]]:
    if not text or not text.strip():
        return False, None

    text_lower = text.strip().lower()

    if len(text_lower) > 60:
        return False, None

    complex_indicators = [
        "how", "why", "what is", "explain", "summarize", "write", "generate",
        "can you", "could you", "help me", "tell me", "?", "please"
    ]
    if any(ind in text_lower for ind in complex_indicators):
        return False, None

    for pattern, action in COMPILED_PATTERNS:
        if pattern.search(text_lower):
            return True, action

    return False, None


def execute_simple_task(action_key: str) -> None:
    # TODO: 实际执行动作，比如调用硬件 API、发 MQTT 消息等
    print(f"[EXECUTE] Performing simple task: {action_key}")
    # 示例：if action_key == "light_on": gpio.turn_on_light()