# tools/weather_tool.py
import requests
from langchain_core.tools import Tool

class WeatherTool:
    def _run(self, location: str) -> str:
        """
        Get current weather for a location.
        For simplicity, we map common city names to coordinates.
        In production, use geocoding (e.g., OpenStreetMap Nominatim).
        """
        # City GIP
        city_coords = {
            "beijing": (39.9042, 116.4074),
            "shanghai": (31.2304, 121.4737),
            "guangzhou": (23.1291, 113.2644),
            "shenzhen": (22.5431, 114.0579),
            "hangzhou": (30.2741, 120.1551),
            "sydney": (-33.8688, 151.2093),
            "default": (-33.8688, 151.2093),  # fallback to Sydney
        }

        loc_key = location.lower().strip()
        lat, lon = city_coords.get(loc_key, city_coords["default"])

        try:
            url = "https://api.open-meteo.com/v1/forecast" 
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": True
            }
            resp = requests.get(url, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current_weather", {})
                temp = current.get("temperature", "N/A")
                windspeed = current.get("windspeed", "N/A")
                weathercode = current.get("weathercode", "N/A")
                # 参考：https://open-meteo.com/en/docs  
                wmo_codes = {
                    0: "Clear sky",
                    1: "Mainly clear",
                    2: "Partly cloudy",
                    3: "Overcast",
                    45: "Fog",
                    48: "Depositing rime fog",
                    51: "Light drizzle",
                    53: "Moderate drizzle",
                    55: "Dense drizzle",
                    61: "Slight rain",
                    63: "Moderate rain",
                    65: "Heavy rain",
                    71: "Slight snow",
                    73: "Moderate snow",
                    75: "Heavy snow",
                    95: "Thunderstorm",
                }
                desc = wmo_codes.get(weathercode, f"Code {weathercode}")
                return f"Current weather in {location}: {desc}, {temp}°C, wind {windspeed} km/h."
            else:
                return f"Weather API error: HTTP {resp.status_code}"
        except Exception as e:
            return f"Failed to fetch weather: {str(e)}"

    def as_tool(self) -> Tool:
        return Tool(
            name="GetWeather",
            func=self._run,
            description=(
                "Get the current weather for a given city. "
                "Input must be a single city name in English (e.g., 'Beijing', 'Shanghai'). "
                "Do not use Chinese names. Only support major Chinese cities and Sydney for now."
            )
        )