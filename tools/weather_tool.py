import requests
import os
import re

API_KEY = os.getenv("WEATHER_API_KEY")  # make sure this is set in .env


def extract_city(query: str) -> str | None:
    """
    Extract city name from user query by looking at the last word(s).
    Handles phrases like 'weather in navsari city' or 'tell me about delhi weather'.
    """
    clean_query = re.sub(r'[^\w\s]', '', query).lower()
    words = clean_query.split()

    ignore_words = {
        "weather", "today", "in", "for", "tell", "me", "what", "is", "about",
        "the", "city", "please", "would", "like", "know", "yes", "i", "want",
        "to", "of", "on", "how", "much", "temperature"
    }

    # Reverse loop → last useful word = city
    for w in reversed(words):
        if w not in ignore_words:
            return w.capitalize()

    return None


def get_weather(query: str) -> str:
    """
    Fetch full weather details for a given query.
    """
    if not API_KEY:
        return "⚠️ WEATHER_API_KEY not found. Please set it in your environment variables."

    city = extract_city(query)
    if not city:
        return "🌍 Please tell me which city you want the weather for."

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()

        if resp.status_code != 200:
            return f"⚠️ Couldn't fetch weather for {city}. ({data.get('message', 'city not found')})"

        # Extract details
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind_speed = data["wind"]["speed"]
        wind_dir = data["wind"].get("deg", "N/A")
        desc = data["weather"][0]["description"].capitalize()
        visibility = data.get("visibility", "N/A")

        return f"""
🌤️ **Weather in {city}:**
- Temperature: {temp}°C (Feels like {feels_like}°C)
- Min/Max: {temp_min}°C / {temp_max}°C
- Condition: {desc}
- Humidity: {humidity}%
- Pressure: {pressure} hPa
- Wind: {wind_speed} m/s, Direction {wind_dir}°
- Visibility: {visibility/1000 if isinstance(visibility, int) else visibility} km
        """
    except Exception as e:
        return f"⚠️ Error fetching weather: {str(e)}"
