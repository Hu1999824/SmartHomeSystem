# tools/time_tool.py

from datetime import datetime
from langchain_core.tools import StructuredTool, BaseTool 
from pydantic import BaseModel

# Key change 2: Define an empty argument model
class GetCurrentTimeArgs(BaseModel):
    """Schema for GetCurrentTime tool, which takes no inputs."""
    pass  # Empty — this tool requires no parameters


# Key change 3: Function signature with no parameters
def _get_current_time() -> str:
    """Get the current date and time."""
    now = datetime.now()
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday = weekday_names[now.weekday()]
    return f"{now.strftime('%Y-%m-%d')} {weekday} {now.strftime('%H:%M:%S')}"


# Key change 4: Return a StructuredTool with explicit args_schema
def as_time_tool() -> BaseTool:
    return StructuredTool(
        name="GetCurrentTime",
        func=_get_current_time,
        description=(
            "Retrieve the current precise date and time, including year, month, day, weekday, hour, minute, and second. "
            "Use this tool when the user asks questions like 'What time is it?', 'What's today's date?', "
            "'What day is it?', or 'What's the current time?'. "
            "This tool requires no input parameters."
        ),
        args_schema=GetCurrentTimeArgs  # Explicitly indicates no arguments are needed
    )