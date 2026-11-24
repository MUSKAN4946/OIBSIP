# Voice Assistant (Beginner Tier)

A Python-based voice assistant that listens to spoken commands and responds with voice. Built as part of the Oasis Infobyte Python Programming Internship (Task 1).

## Features

- Captures voice input from the microphone using `speech_recognition`
- Responds to "hello" with a greeting
- Tells the current time and date
- Searches the web on any topic (opens Google in the browser)
- Handles errors gracefully: asks the user to repeat if the voice is not understood
- Speaks every response using `pyttsx3` (text-to-speech)

## Tech Stack

- Python 3.12
- speech_recognition
- pyttsx3
- PyAudio
- datetime, webbrowser

## Installation

```
py -3.12 -m pip install SpeechRecognition pyttsx3 pyaudio
```

## How to Run

```
py -3.12 assistant.py
```

## Voice Commands

| Say this | What happens |
|---|---|
| "hello" | Assistant greets you |
| "what is the time" | Tells the current time |
| "what is the date" | Tells today's date |
| "search for python tutorial" | Opens a Google search in the browser |
| "stop" or "exit" | Closes the assistant |

## Privacy Note

Your voice is captured from the microphone and sent to Google's free speech recognition service to convert it into text. Nothing is stored on disk by this project.

## Author

Muskan Verma