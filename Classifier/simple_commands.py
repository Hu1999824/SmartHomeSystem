# Format: (tuple_of_phrases, action_key)
SIMPLE_COMMANDS = {
    ("turn on the light", "light on", "switch on the light", "enable light"): "light_on",
    ("turn off the light", "light off", "switch off the light", "disable light"): "light_off",

        # Air Conditioner
    ("turn on the air conditioner", "turn on ac", "ac on", "start cooling", "enable ac"): "ac_on",
    ("turn off the air conditioner", "turn off ac", "ac off", "disable ac"): "ac_off",
    ("increase temperature", "temperature up", "make it warmer", "raise temperature"): "ac_temp_up",
    ("decrease temperature", "temperature down", "make it cooler", "lower temperature"): "ac_temp_down",
    ("set temperature to", "set ac temperature to", "set air conditioner to"): "ac_set_temp",

    # Curtain
    ("open curtain", "draw curtain", "open the curtain", "raise curtain"): "curtain_open",
    ("close curtain", "shut curtain", "lower curtain"): "curtain_close",

    # TV
    ("turn on tv", "tv on", "switch on tv", "enable tv", "open tv"): "tv_on",
    ("turn off tv", "tv off", "switch off tv", "disable tv", "close tv"): "tv_off",
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