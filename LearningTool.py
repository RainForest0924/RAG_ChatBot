from langchain_core.tools import tool

@tool
def get_current_weather(location: str) -> str:
    """Get the current weather in a given location"""
    # Here you would implement the logic to get the current weather for the location
    return f"The current weather in {location} is sunny with a temperature of 25°C."