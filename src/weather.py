"""
Weather data fetching for Kindle Dashboard.
Uses Open-Meteo API (free, no API key required).
"""

import urllib.request
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Weather code to description and icon mapping
# Based on WMO Weather interpretation codes
WEATHER_CODES = {
    0: ("Clear", "☀"),
    1: ("Mainly Clear", "🌤"),
    2: ("Partly Cloudy", "⛅"),
    3: ("Overcast", "☁"),
    45: ("Foggy", "🌫"),
    48: ("Fog", "🌫"),
    51: ("Light Drizzle", "🌧"),
    53: ("Drizzle", "🌧"),
    55: ("Dense Drizzle", "🌧"),
    61: ("Slight Rain", "🌧"),
    63: ("Rain", "🌧"),
    65: ("Heavy Rain", "🌧"),
    71: ("Slight Snow", "🌨"),
    73: ("Snow", "🌨"),
    75: ("Heavy Snow", "🌨"),
    77: ("Snow Grains", "🌨"),
    80: ("Slight Showers", "🌦"),
    81: ("Showers", "🌦"),
    82: ("Violent Showers", "⛈"),
    85: ("Snow Showers", "🌨"),
    86: ("Heavy Snow Showers", "🌨"),
    95: ("Thunderstorm", "⛈"),
    96: ("Thunderstorm w/ Hail", "⛈"),
    99: ("Severe Thunderstorm", "⛈"),
}


def fetch_weather(
    latitude: float,
    longitude: float,
    unit: str = "fahrenheit",
    forecast_hours: int = 12
) -> Optional[Dict[str, Any]]:
    """
    Fetch current weather and forecast from Open-Meteo API.

    Args:
        latitude: Location latitude
        longitude: Location longitude
        unit: "fahrenheit" or "celsius"
        forecast_hours: Number of hours to forecast

    Returns:
        Dictionary with weather data or None if failed
    """

    temp_unit = "fahrenheit" if unit == "fahrenheit" else "celsius"

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        f"&hourly=temperature_2m,weather_code"
        f"&temperature_unit={temp_unit}"
        f"&wind_speed_unit=mph"
        f"&forecast_hours={forecast_hours}"
        f"&timezone=auto"
    )

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Weather fetch error: {e}")
        return None

    # Parse current weather
    current = data.get("current", {})
    weather_code = current.get("weather_code", 0)
    description, icon = WEATHER_CODES.get(weather_code, ("Unknown", "?"))

    result = {
        "current": {
            "temperature": round(current.get("temperature_2m", 0)),
            "humidity": current.get("relative_humidity_2m", 0),
            "wind_speed": round(current.get("wind_speed_10m", 0)),
            "weather_code": weather_code,
            "description": description,
            "icon": icon,
        },
        "unit": "°F" if unit == "fahrenheit" else "°C",
        "hourly": [],
    }

    # Parse hourly forecast
    hourly = data.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    codes = hourly.get("weather_code", [])

    for i, (time_str, temp, code) in enumerate(zip(times, temps, codes)):
        if i >= forecast_hours:
            break

        dt = datetime.fromisoformat(time_str)
        desc, ico = WEATHER_CODES.get(code, ("Unknown", "?"))

        result["hourly"].append({
            "time": dt.strftime("%-I%p").lower(),
            "hour": dt.hour,
            "temperature": round(temp),
            "weather_code": code,
            "description": desc,
            "icon": ico,
        })

    # Calculate high/low for the forecast period
    if temps:
        result["high"] = round(max(temps[:forecast_hours]))
        result["low"] = round(min(temps[:forecast_hours]))

    return result


def format_weather_text(weather: Dict[str, Any]) -> str:
    """Format weather data as human-readable text."""

    if not weather:
        return "Weather unavailable"

    c = weather["current"]
    unit = weather["unit"]

    lines = [
        f"{c['icon']} {c['temperature']}{unit} - {c['description']}",
        f"H: {weather.get('high', '--')}{unit}  L: {weather.get('low', '--')}{unit}",
        f"Humidity: {c['humidity']}%  Wind: {c['wind_speed']} mph",
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    # Test with Dallas, TX coordinates
    weather = fetch_weather(32.7767, -96.7970)
    if weather:
        print(format_weather_text(weather))
        print("\nHourly forecast:")
        for h in weather["hourly"][:6]:
            print(f"  {h['time']}: {h['temperature']}°F {h['icon']}")
    else:
        print("Failed to fetch weather")
