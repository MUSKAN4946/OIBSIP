import os

import requests
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")
API_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(location):
    """Fetch weather data for a city name or an Indian ZIP (PIN) code."""
    params = {"appid": API_KEY, "units": "metric"}

    # If the input is only digits, treat it as a ZIP code (India by default)
    if location.isdigit():
        params["zip"] = location + ",IN"
    else:
        params["q"] = location

    try:
        response = requests.get(API_URL, params=params, timeout=10)
    except requests.exceptions.Timeout:
        print("Error: The request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException:
        print("Error: Network problem. Please check your internet connection.")
        return None

    if response.status_code == 200:
        return response.json()
    if response.status_code == 404:
        print("Error: City or ZIP code not found. Please check the spelling.")
    elif response.status_code == 401:
        print("Error: Invalid API key. Please check your .env file.")
    else:
        print("Error: The weather service returned an error (code " + str(response.status_code) + ").")
    return None


def show_weather(data):
    """Print the weather details in a clean format."""
    city = data["name"]
    country = data["sys"]["country"]
    temp_c = data["main"]["temp"]
    temp_f = temp_c * 9 / 5 + 32
    humidity = data["main"]["humidity"]
    description = data["weather"][0]["description"].title()
    wind = data["wind"]["speed"]

    print()
    print("Weather in " + city + ", " + country)
    print("-" * 32)
    print("Temperature : " + str(round(temp_c, 1)) + " C / " + str(round(temp_f, 1)) + " F")
    print("Humidity    : " + str(humidity) + " %")
    print("Condition   : " + description)
    print("Wind speed  : " + str(wind) + " m/s")
    print()


def main():
    if not API_KEY:
        print("Error: WEATHER_API_KEY is missing. Please check your .env file.")
        return

    print("=== Weather App ===")

    while True:
        location = input("Enter a city name or ZIP code (or type 'exit' to quit): ").strip()

        if location == "":
            print("Error: Input cannot be empty. Please enter a city name or ZIP code.")
            continue

        if location.lower() == "exit":
            print("Goodbye!")
            break

        data = get_weather(location)
        if data:
            show_weather(data)


if __name__ == "__main__":
    main()