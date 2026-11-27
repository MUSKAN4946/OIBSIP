# Voice Assistant (Beginner + Advanced Tier)

A Python-based voice assistant that listens to spoken commands and replies with voice. It understands free-form sentences and can fetch live weather, send emails, set reminders and answer general knowledge questions. Built as part of the Oasis Infobyte Python Programming Internship (Task 1).

## Features

**Beginner**
- Captures voice input from the microphone using `speech_recognition`
- Responds to "hello" with a greeting
- Tells the current time and date
- Searches the web on any topic (opens Google in the browser)
- Asks the user to repeat if the voice is not understood
- Speaks every response using `pyttsx3` (text-to-speech)

**Advanced**
- Natural language understanding: detects the intent of free-form sentences using `nltk` (word stemming and keyword scoring), not just exact keywords
- Sends an email by voice using `smtplib` (Gmail SMTP with an App Password)
- Timed reminders with an audible beep alert
- Live weather updates using the OpenWeatherMap API
- General knowledge answers using the Wikipedia API
- Custom commands: add your own commands in `commands.json` without changing the code

## Tech Stack

- Python 3.12
- speech_recognition, PyAudio
- pyttsx3
- nltk
- requests
- python-dotenv
- smtplib, datetime, webbrowser, threading, json

## Installation

```
py -3.12 -m pip install SpeechRecognition pyaudio pyttsx3 nltk requests python-dotenv
```

## Setup

Create a file named `.env` in this folder with your own keys (this file is ignored by Git and is never uploaded):

```
WEATHER_API_KEY=your_openweathermap_key
EMAIL_ADDRESS=your_test_gmail_address
EMAIL_PASSWORD=your_gmail_app_password
EMAIL_RECEIVER=email_that_receives_the_mail
```

Use a test or dummy Gmail account for sending emails, not your main account.

## How to Run

```
py -3.12 assistant.py
```

## Voice Commands

| Say something like | What happens |
|---|---|
| "hello" | Assistant greets you |
| "can you tell me what time it is" | Tells the current time |
| "what is the date today" | Tells today's date |
| "weather in Bhopal" | Tells temperature, condition, humidity and wind speed |
| "remind me in 10 seconds" | Beeps and shows a reminder after the given time |
| "send email" | Asks for a subject and message, then sends the email |
| "who is Albert Einstein" | Reads a short summary from Wikipedia |
| "search for python tutorial" | Opens a Google search in the browser |
| "open YouTube" | Runs a custom command from `commands.json` |
| "stop" or "exit" | Closes the assistant |

## Custom Commands

Open `commands.json` and add your own entries. Example:

```json
"open google": {
  "type": "url",
  "target": "https://www.google.com",
  "reply": "Opening Google"
}
```

Use `"type": "url"` to open a website, or `"type": "say"` to only speak a reply. No code change is needed.

## Privacy: Data Processed and How

- **Voice audio:** captured from your microphone and sent to Google's free Web Speech API to convert it into text. It is not saved on your computer.
- **Weather:** the city name you say is sent to OpenWeatherMap.
- **General knowledge:** the topic you say is sent to Wikipedia.
- **Email:** the subject and message you say are sent through Gmail's SMTP server to the receiver address set in `.env`.
- **Secrets:** API keys and the email App Password are stored only in your local `.env` file, which is listed in `.gitignore` and is never pushed to GitHub.
- **Local files:** the assistant does not save voice recordings or conversation history to disk. `commands.json` only stores the custom commands you write yourself.
- Because Google, OpenWeatherMap, Wikipedia and Gmail are used, an internet connection is required and your requests are processed by those services under their own privacy policies.

## Author

Muskan Verma