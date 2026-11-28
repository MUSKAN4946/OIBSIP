import os
import tkinter as tk
from datetime import datetime, timedelta, timezone
from io import BytesIO

import requests
from dotenv import load_dotenv
from PIL import Image, ImageTk

# Load the API key from the .env file
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ICON_URL = "https://openweathermap.org/img/wn/{code}@2x.png"

BG = "#0B1220"
CARD = "#16213A"
TEXT = "#F4F6FB"
MUTED = "#9FB0CC"
ACCENT = "#F26B3A"
ERROR = "#FF6B6B"


class WeatherApp:
    def __init__(self, root):
        self.root = root
        root.title("Weather App")
        root.geometry("580x880")
        root.configure(bg=BG)
        root.resizable(False, False)

        # Keep references to images, otherwise tkinter removes them
        self.icon_image = None
        self.small_icons = []
        self.icon_cache = {}

        # Data is stored in Celsius and converted only when shown
        self.unit = "C"
        self.weather_data = None
        self.forecast_data = None

        tk.Label(root, text="Weather App", font=("Segoe UI", 22, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(16, 8))

        # Input row
        input_row = tk.Frame(root, bg=BG)
        input_row.pack(pady=(0, 4))
        self.city_entry = tk.Entry(input_row, font=("Segoe UI", 14), width=24,
                                   bg=CARD, fg=TEXT, insertbackground=TEXT,
                                   relief="flat")
        self.city_entry.pack(side="left", ipady=6, padx=(0, 8))
        self.city_entry.focus()
        self.city_entry.bind("<Return>", lambda event: self.get_weather())

        tk.Button(input_row, text="Get Weather", font=("Segoe UI", 11, "bold"),
                  bg=ACCENT, fg="white", activebackground="#d85a2b",
                  activeforeground="white", relief="flat", cursor="hand2",
                  command=self.get_weather).pack(side="left", ipady=4, ipadx=8)

        # Unit toggle button
        self.unit_button = tk.Button(root, text="Switch to \u00b0F", font=("Segoe UI", 10, "bold"),
                                     bg=CARD, fg=TEXT, activebackground=ACCENT,
                                     activeforeground="white", relief="flat",
                                     cursor="hand2", command=self.toggle_unit)
        self.unit_button.pack(pady=(4, 0), ipadx=10, ipady=2)

        # Error message area (errors are shown inside the window)
        self.error_label = tk.Label(root, text="", font=("Segoe UI", 11),
                                    bg=BG, fg=ERROR, wraplength=520)
        self.error_label.pack(pady=(2, 4))

        # Current weather panel
        self.result_frame = tk.Frame(root, bg=CARD)
        self.result_frame.pack(padx=30, pady=4, fill="x")

        self.city_label = tk.Label(self.result_frame, text="", font=("Segoe UI", 16, "bold"),
                                   bg=CARD, fg=TEXT)
        self.city_label.pack(pady=(10, 0))

        self.icon_label = tk.Label(self.result_frame, bg=CARD)
        self.icon_label.pack()

        self.temp_label = tk.Label(self.result_frame, text="--", font=("Segoe UI", 38, "bold"),
                                   bg=CARD, fg=ACCENT)
        self.temp_label.pack()

        self.condition_label = tk.Label(self.result_frame, text="", font=("Segoe UI", 13),
                                        bg=CARD, fg=TEXT)
        self.condition_label.pack(pady=(0, 4))

        self.humidity_label = tk.Label(self.result_frame, text="", font=("Segoe UI", 11),
                                       bg=CARD, fg=MUTED)
        self.humidity_label.pack(pady=1)

        self.wind_label = tk.Label(self.result_frame, text="", font=("Segoe UI", 11),
                                   bg=CARD, fg=MUTED)
        self.wind_label.pack(pady=(1, 10))

        # Hourly forecast panel
        tk.Label(root, text="Next 6 hours", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", padx=34, pady=(8, 4))
        self.hourly_frame = tk.Frame(root, bg=BG)
        self.hourly_frame.pack(padx=30, fill="x")

        # Daily forecast panel
        tk.Label(root, text="Next 5 days", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=TEXT).pack(anchor="w", padx=34, pady=(10, 4))
        self.daily_frame = tk.Frame(root, bg=BG)
        self.daily_frame.pack(padx=30, fill="x")

    # ---------- Unit handling ----------
    def convert(self, celsius):
        """Return the temperature as a rounded number in the selected unit."""
        if self.unit == "F":
            return round(celsius * 9 / 5 + 32)
        return round(celsius)

    def symbol(self):
        return "\u00b0" + self.unit

    def toggle_unit(self):
        """Switch between Celsius and Fahrenheit without calling the API again."""
        if self.unit == "C":
            self.unit = "F"
            self.unit_button.config(text="Switch to \u00b0C")
        else:
            self.unit = "C"
            self.unit_button.config(text="Switch to \u00b0F")

        if self.weather_data:
            self.display_weather(self.weather_data)
        if self.forecast_data:
            self.render_forecast()

    # ---------- Helpers ----------
    def show_error(self, message):
        self.error_label.config(text=message)

    def clear_forecast(self):
        for frame in (self.hourly_frame, self.daily_frame):
            for widget in frame.winfo_children():
                widget.destroy()
        self.small_icons = []

    def clear_results(self):
        self.weather_data = None
        self.forecast_data = None
        self.city_label.config(text="")
        self.icon_label.config(image="")
        self.icon_image = None
        self.temp_label.config(text="--")
        self.condition_label.config(text="")
        self.humidity_label.config(text="")
        self.wind_label.config(text="")
        self.clear_forecast()

    def get_icon(self, code, size):
        """Download a weather icon (cached). Returns None if it fails."""
        key = (code, size)
        if key in self.icon_cache:
            return self.icon_cache[key]
        try:
            response = requests.get(ICON_URL.format(code=code), timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content)).resize((size, size))
            photo = ImageTk.PhotoImage(image)
            self.icon_cache[key] = photo
            return photo
        except (requests.exceptions.RequestException, OSError):
            return None

    # ---------- Fetching data ----------
    def get_weather(self):
        location = self.city_entry.get().strip()
        self.show_error("")

        if location == "":
            self.show_error("Please enter a city name or ZIP code.")
            return

        if not API_KEY:
            self.show_error("API key is missing. Please check your .env file.")
            return

        params = {"appid": API_KEY, "units": "metric"}
        if location.isdigit():
            params["zip"] = location + ",IN"
        else:
            params["q"] = location

        try:
            response = requests.get(CURRENT_URL, params=params, timeout=10)
        except requests.exceptions.Timeout:
            self.clear_results()
            self.show_error("The request timed out. Please try again.")
            return
        except requests.exceptions.RequestException:
            self.clear_results()
            self.show_error("Network problem. Please check your internet connection.")
            return

        if response.status_code == 404:
            self.clear_results()
            self.show_error("City or ZIP code not found. Please check the spelling.")
            return
        if response.status_code == 401:
            self.clear_results()
            self.show_error("Invalid API key. Please check your .env file.")
            return
        if response.status_code != 200:
            self.clear_results()
            self.show_error("The weather service returned an error (code "
                            + str(response.status_code) + ").")
            return

        self.weather_data = response.json()
        self.display_weather(self.weather_data)
        self.load_forecast(params)

    def load_forecast(self, params):
        """Fetch the forecast once and use it for both hourly and daily panels."""
        self.clear_forecast()
        self.forecast_data = None
        try:
            response = requests.get(FORECAST_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            data["city"]["timezone"]  # make sure the data has what we need
            self.forecast_data = data
        except (requests.exceptions.RequestException, ValueError, KeyError):
            self.show_error("Could not load the forecast.")
            return
        self.render_forecast()

    # ---------- Showing data ----------
    def display_weather(self, data):
        city = data["name"] + ", " + data["sys"]["country"]
        condition = data["weather"][0]["description"].title()
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        self.city_label.config(text=city)
        self.temp_label.config(text=str(self.convert(data["main"]["temp"])) + self.symbol())
        self.condition_label.config(text=condition)
        self.humidity_label.config(text="Humidity: " + str(humidity) + " %")
        self.wind_label.config(text="Wind speed: " + str(wind) + " m/s")

        self.icon_image = self.get_icon(data["weather"][0]["icon"], 80)
        self.icon_label.config(image=self.icon_image if self.icon_image else "")

    def render_forecast(self):
        self.clear_forecast()
        offset = self.forecast_data["city"]["timezone"]  # seconds from UTC for this city
        self.show_hourly(self.forecast_data, offset)
        self.show_daily(self.forecast_data, offset)

    def make_card(self, parent, title, icon_code, bottom_text):
        card = tk.Frame(parent, bg=CARD)
        card.pack(side="left", expand=True, fill="both", padx=4)

        tk.Label(card, text=title, font=("Segoe UI", 11, "bold"),
                 bg=CARD, fg=TEXT).pack(pady=(8, 0))

        icon = self.get_icon(icon_code, 52)
        if icon:
            self.small_icons.append(icon)
            tk.Label(card, image=icon, bg=CARD).pack()

        tk.Label(card, text=bottom_text, font=("Segoe UI", 11, "bold"),
                 bg=CARD, fg=ACCENT).pack(pady=(0, 8))

    def show_hourly(self, data, offset):
        """Show the next 3 forecast slots (3 hours apart = about 6 hours)."""
        for item in data["list"][:3]:
            local_time = datetime.fromtimestamp(item["dt"] + offset, tz=timezone.utc)
            time_text = local_time.strftime("%I %p").lstrip("0")
            temp = self.convert(item["main"]["temp"])
            self.make_card(self.hourly_frame, time_text, item["weather"][0]["icon"],
                           str(temp) + self.symbol())

    def show_daily(self, data, offset):
        """Group the 3-hour forecast by day and show the next 5 days."""
        today = (datetime.now(timezone.utc) + timedelta(seconds=offset)).date()
        days = {}

        for item in data["list"]:
            local_time = datetime.fromtimestamp(item["dt"] + offset, tz=timezone.utc)
            if local_time.date() == today:
                continue
            days.setdefault(local_time.date(), []).append((local_time, item))

        for day in sorted(days)[:5]:
            entries = days[day]
            high = self.convert(max(item["main"]["temp_max"] for _, item in entries))
            low = self.convert(min(item["main"]["temp_min"] for _, item in entries))
            # Use the icon of the forecast closest to 12 noon
            best_item = min(entries, key=lambda entry: abs(entry[0].hour - 12))[1]
            self.make_card(self.daily_frame, day.strftime("%a"),
                           best_item["weather"][0]["icon"],
                           str(high) + "\u00b0 / " + str(low) + "\u00b0")


def main():
    root = tk.Tk()
    WeatherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()