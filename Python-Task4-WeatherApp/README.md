# Weather App (Beginner + Advanced Tier)

A Python application that fetches and displays real-time weather data for any city or ZIP code using the OpenWeatherMap API. It comes in two versions: a command-line app (Beginner) and a graphical app with icons and forecasts (Advanced). Built as part of the Oasis Infobyte Python Programming Internship (Task 4).

## Features

**Beginner (`weather.py`)**
- Asks for a city name or ZIP code
- Calls the OpenWeatherMap API and parses the JSON response
- Shows temperature (°C and °F), humidity, weather condition and wind speed
- Handles errors: city not found, network timeout, invalid API key
- Rejects empty input

**Advanced (`weather_gui.py`)**
- GUI window built with `tkinter`: city input field, "Get Weather" button and a results panel
- Weather icons for the current condition and for every forecast card
- Hourly forecast: the next 6 hours (three 3-hour slots, the smallest step the free API gives)
- Daily forecast: the next 5 days with high and low temperatures
- Celsius / Fahrenheit switch button (works without calling the API again)
- Error messages are shown inside the window, not in the terminal

## Tech Stack

- Python 3.12
- requests
- python-dotenv
- tkinter
- Pillow (PIL)
- OpenWeatherMap API (free tier)

## Installation

```
py -3.12 -m pip install requests python-dotenv pillow
```

`tkinter` comes with Python, so it does not need a separate install.

## Setup

1. Get a free API key from [openweathermap.org](https://openweathermap.org/api).
2. Create a file named `.env` in this folder:

```
WEATHER_API_KEY=your_openweathermap_key
```

This file is listed in `.gitignore`, so your key is never uploaded to GitHub.

## How to Run

Command-line version:

```
py -3.12 weather.py
```

GUI version:

```
py -3.12 weather_gui.py
```

## How to Use

1. Type a city name (for example `Bhopal`) or a ZIP code (for example `462001`) and press Enter or click **Get Weather**.
2. Click **Switch to °F** to change the temperature unit, and click again to switch back.
3. In the command-line version, type `exit` to quit.

Note: a number-only input is treated as an Indian PIN code.

## Privacy Note

The city name or ZIP code you enter is sent to the OpenWeatherMap API to get the weather. Weather icons are downloaded from openweathermap.org. The app does not save your searches or any personal data. Your API key stays only in your local `.env` file.

## Author

Muskan Verma