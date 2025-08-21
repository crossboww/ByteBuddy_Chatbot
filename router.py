from tools.weather_tool import get_weather
# future: from tools.lyrics_tool import get_lyrics
# future: from tools.news_tool import get_news

def route_query(query: str):
    query = query.lower()

    if "weather" in query or "temperature" in query:
        return "weather"
    # elif "lyrics" in query or "song" in query:
    #     return "lyrics"
    # elif "news" in query:
    #     return "news"
    else:
        return "chat"


def handle_user_query(user_input: str, messages: list, llm_callback):
    """
    Routes the user query:
      - Weather → calls weather tool
      - Else → calls LLM with full chat history
    """
    tool = route_query(user_input)

    if tool == "weather":
        return get_weather(user_input)

    # elif tool == "lyrics":
    #     return get_lyrics(user_input)

    # elif tool == "news":
    #     return get_news(user_input)

    else:
        return llm_callback(messages)
