import datetime
import re
import threading
import webbrowser
import winsound

import pyttsx3
import speech_recognition as sr

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


def main():
    speak("Hello, I am your voice assistant. How can I help you?")

    while True:
        command = listen()

        if command == "":
            continue

        if "hello" in command:
            speak("Hello! Nice to meet you.")
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