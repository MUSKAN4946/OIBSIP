import datetime
import os
import re
import smtplib
import threading
import webbrowser
import winsound
from email.message import EmailMessage

import pyttsx3
import requests
import speech_recognition as sr
from dotenv import load_dotenv

# Load secrets from the .env file
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Setup text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 170)

# Setup speech recognizer
recognizer = sr.Recognizer()


def speak(text):
    """Print the text and speak it out loud."""
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()


def listen():
    """Listen from the microphone and return the text in lowercase."""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text.lower()
        except sr.WaitTimeoutError:
            speak("I did not hear anything. Please try again.")
        except sr.UnknownValueError:
            speak("Sorry, I could not understand. Please repeat.")
        except sr.RequestError:
            speak("Network error. Please check your internet connection.")
    return ""


def tell_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    speak("The current time is " + now)


def tell_date():
    today = datetime.datetime.now().strftime("%A, %d %B %Y")
    speak("Today is " + today)


def web_search(command):
    # Remove the word "search" (and "for") to get only the topic
    query = command.replace("search for", "").replace("search", "").strip()

    if query == "":
        speak("What do you want to search for?")
        query = listen()
        if query == "":
            return

    speak("Searching for " + query)
    webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))


def reminder_alert(message):
    """Called when the reminder time is over: beep and print the message."""
    print("\n*** REMINDER: " + message + " ***")
    for _ in range(3):
        winsound.Beep(1000, 500)


def set_reminder(command):
    # Find a number and a unit in the command, e.g. "10 seconds" or "2 minutes"
    match = re.search(r"(\d+)\s*(second|seconds|minute|minutes|hour|hours)", command)

    if not match:
        speak("Please say the time clearly. For example, remind me in 10 seconds.")
        return

    amount = int(match.group(1))
    unit = match.group(2)

    if unit.startswith("second"):
        seconds = amount
    elif unit.startswith("minute"):
        seconds = amount * 60
    else:
        seconds = amount * 3600

    timer = threading.Timer(seconds, reminder_alert, args=["Your reminder time is over!"])
    timer.daemon = True
    timer.start()
    speak("Okay, I will remind you in " + str(amount) + " " + unit)


def get_weather(command):
    if not WEATHER_API_KEY:
        speak("Weather API key is missing. Please check your .env file.")
        return

    # Find the city name after the words "in", "of" or "for"
    match = re.search(r"weather (?:in|of|for) (.+)", command)
    if match:
        city = match.group(1).strip()
        city = city.split(" what")[0].strip()
    else:
        speak("Which city's weather do you want?")
        city = listen()
        if city == "":
            return

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if response.status_code == 200:
            temp = round(data["main"]["temp"])
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            condition = data["weather"][0]["description"]
            speak(
                "In " + city + ", it is " + str(temp) + " degrees Celsius with "
                + condition + ". Humidity is " + str(humidity)
                + " percent and wind speed is " + str(wind) + " meters per second."
            )
        elif response.status_code == 404:
            speak("Sorry, I could not find the city " + city + ".")
        elif response.status_code == 401:
            speak("The API key is not valid yet. Please check it or wait a little.")
        else:
            speak("Sorry, the weather service gave an error.")
    except requests.exceptions.Timeout:
        speak("The weather service took too long to respond.")
    except requests.exceptions.RequestException:
        speak("Network error. Please check your internet connection.")


def send_email():
    if not (EMAIL_ADDRESS and EMAIL_PASSWORD and EMAIL_RECEIVER):
        speak("Email settings are missing. Please check your .env file.")
        return

    speak("What is the subject of the email?")
    subject = listen()
    if subject == "":
        return

    speak("What is the message?")
    body = listen()
    if body == "":
        return

    message = EmailMessage()
    message["From"] = EMAIL_ADDRESS
    message["To"] = EMAIL_RECEIVER
    message["Subject"] = subject
    message.set_content(body)

    try:
        # App passwords are shown with spaces, so remove them
        password = EMAIL_PASSWORD.replace(" ", "")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(EMAIL_ADDRESS, password)
            server.send_message(message)
        speak("Your email has been sent successfully.")
    except smtplib.SMTPAuthenticationError:
        speak("Email login failed. Please check the email and app password.")
    except Exception:
        speak("Sorry, I could not send the email. Please check your internet connection.")


def main():
    speak("Hello, I am your voice assistant. How can I help you?")

    while True:
        command = listen()

        if command == "":
            continue

        if "hello" in command:
            speak("Hello! Nice to meet you.")
        elif "email" in command:
            send_email()
        elif "weather" in command:
            get_weather(command)
        elif "remind" in command or "reminder" in command:
            set_reminder(command)
        elif "time" in command:
            tell_time()
        elif "date" in command:
            tell_date()
        elif "search" in command:
            web_search(command)
        elif "exit" in command or "stop" in command:
            speak("Goodbye! Have a nice day.")
            break
        else:
            speak("Sorry, I do not know that command yet.")


if __name__ == "__main__":
    main()