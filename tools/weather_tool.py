import requests
import os

API_KEY = os.getenv("WEATHER_API_KEY")  # set this in your .env file

def get_weather(query: str) -> str:
    """
    Extract city name from user query and fetch weather using OpenWeather API.
    If no city is found, returns a helpful message.
    """
    if not API_KEY:
        return "⚠️ WEATHER_API_KEY not found. Please set it in your environment variables."

    # 🔹 Basic city extraction (later we can improve with NLP or regex)
    words = query.split()
    city = None
    for w in words:
        if w.istitle():  # assume capitalized word = city name
            city = w
            break

    if not city:
        return "🌍 Please specify a city (e.g., 'What's the weather in Delhi?')."

    # 🔹 OpenWeather API call
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()

        if resp.status_code != 200:
            return f"⚠️ Error: {data.get('message', 'Unable to fetch weather')}"

        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]

        return f"🌤️ Weather in **{city}**: {temp}°C, {desc.capitalize()}."
    except Exception as e:
        return f"⚠️ Error fetching weather: {str(e)}"
