# tools/homeassistant_tool.py
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from device.deviceController import DeviceController

class HomeAssistantAction(BaseModel):
    command: str = Field(
        description="The action to perform: 'turn_on', 'turn_off', or 'get_state'"
    )
    entity_id: str = Field(
        description="The full entity ID, e.g., 'light.living_room', 'switch.heater'"
    )

class HomeAssistantTool:
    def __init__(self, device_controller: DeviceController):
        self.device_ctrl = device_controller

    def _run(self, command: str, entity_id: str) -> str:
        command = command.strip().lower()
        entity_id = entity_id.strip()

        if command == "get_state":
            return self.device_ctrl.getDeviceStatus(entity_id)
        elif command in ("turn_on", "turn_off"):
            return self.device_ctrl.executeCommand(entity_id, command)
        else:
            return f"Error: Unsupported command '{command}'. Use 'turn_on', 'turn_off', or 'get_state'."

    def as_tool(self) -> StructuredTool:
        return StructuredTool.from_function(
            func=self._run,
            name="HomeAssistantControl",
            description=(
                "Control or query smart home devices."
            ),
            args_schema=HomeAssistantAction,
        )