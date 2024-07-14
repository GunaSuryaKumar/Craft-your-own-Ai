#Here we are importing text to speech converter in python --pip install pyttsx3
import pyttsx3

#Here we are importing datetime library in python --predifined library
import datetime

#Here we are importing speech recognition library in python --pip install SpeechRecognition
import speech_recognition as sr

#Here we are immporting pyscreeze library in python --pip install pyscreeze & --pip install pillow to take screenshot
import pyscreeze as ss

# Description: This file contains the code to interact with the Eden AI API to get the response from the chatbot.
import json
import requests

# Import the OpenAI library --pip install openai
import openai

headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTgyMGQ5MTAtYzgxNy00YTg1LTg0YjQtZDc4ZmZlNWE3YTczIiwidHlwZSI6ImFwaV90b2tlbiJ9.Kpz0A3TcrtSomCwXupQOMKgjjF3EE2QN43f_Y5PUnkw"}

url = "https://api.edenai.run/v2/text/chat"
payload = {
    "providers": "openai",
    "text": "Hello i need your help ! ",
    "chatbot_global_action": "Act as an assistant",
    "previous_history": [],
    "temperature": 0.0,
    "max_tokens": 150,
    "fallback_providers": "Ai"
}

k = pyttsx3.init()

#Here we are defining a function to talk to the AI
def talktoai(query):
    payload["text"]=query
    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    result = json.loads(response.text)
    speak(result['openai']['generated_text'])

#Here we are defining a function to convert text to speech
def speak(audio):
    k.say(audio)
    k.runAndWait()
speak("Hello, I am AI .")

#Here we are defining a function to tell the current time
def time():
    t = datetime.datetime.now().strftime("%H:%M:%S")
    #print(t)
    speak("Current time is"+t)

#Here we are defining a function to tell the current date
def date():
    y = str(datetime.datetime.now().year)
    m = str(datetime.datetime.now().month)
    d = str(datetime.datetime.now().day)
    #print(y)
    speak("Today's date is" + d + m + y)

#Here we are defining a function to wish the user
def wishme():
    #speak("Welcome back sir!")
    date()
    hour = datetime.datetime.now().hour
    if hour >= 6 and hour < 12:
        speak("Good Morning Sir!")
    elif hour >= 12 and hour < 16:
        speak("Good Afternoon Sir!")
    elif hour >= 16 and hour < 20:
        speak("Good Evening Sir!")
    else:
        speak("Good Night Sir!")
    time()
    speak("I am A I, I am  at your service. Please tell me how can I help you today?")
wishme()

#Here we are defining a function to take command from the user
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        #--pip install pyaudio (this is used to install the pyaudio library in python to work with microphone)
        #--pip install setuptools (this is used to install the setuptools library in python to work with microphone)
        audio = r.listen(source)
    try:
        print("Recognizing...")
        #Here we are using google speech recognition to convert the speech to text
        query = r.recognize_google(audio, language='en-in')
        print(query)
    except Exception as e:
        print(e)
        speak("Say that again please...")
        return "None"
    return query
takeCommand()

#Here we are defining a function to take screenshot
def screenshot():
    img = ss.screenshot()
    img1 = ss.screenshot("screenshot.png")

#Here we are defining the main function
if __name__ == "__main__":
    #wishme()
    while True:
        query = takeCommand().lower()

        if 'time' in query:
            time()

        elif 'date' in query:
            date()

        elif 'screenshot' in query:
            try:
                screenshot()
                speak("Screenshot taken.")
            except Exception as e:
                print(e)
                speak("I'm sorry, I couldn't take the screenshot.")

        elif 'exit' in query:
            speak("Thankyou for using . Have a nice day!")
            print("Restart the program to use again.")
            quit()
        
        else:
            talktoai(query)