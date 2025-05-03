import pyttsx3
import datetime
import speech_recognition as sr
import pyscreeze as ss
import json
import requests
from flask import Flask, render_template, request, jsonify
import os
import sqlite3
from datetime import datetime
import re

# Initialize Flask app
app = Flask(__name__)

# Initialize text-to-speech (disabled on Render due to no audio support)
try:
    k = pyttsx3.init()
except:
    k = None

# Eden AI API configuration
headers = {
    "Authorization": f"Bearer {os.getenv('EDEN_AI_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTgyMGQ5MTAtYzgxNy00YTg1LTg0YjQtZDc4ZmZlNWE3YTczIiwidHlwZSI6ImFwaV90b2tlbiJ9.Kpz0A3TcrtSomCwXupQOMKgjjF3EE2QN43f_Y5PUnkw')}"
}
url = "https://api.edenai.run/v2/text/chat"
payload = {
    "providers": "openai",
    "text": "",
    "chatbot_global_action": "Act as an assistant",
    "previous_history": [],
    "temperature": 0.0,
    "max_tokens": 150,
    "fallback_providers": "Ai"
}

# Database setup for notes (use temporary directory for Render)
def init_db():
    db_path = os.path.join('/tmp', 'notes.db') if os.getenv('RENDER') else 'notes.db'
    with sqlite3.connect(db_path) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS notes
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    return db_path

# Speak function (disabled on Render)
def speak(audio):
    if k and not os.getenv('RENDER'):
        k.say(audio)
        k.runAndWait()

# AI interaction
def talktoai(query):
    payload["text"] = query
    try:
        response = requests.post(url, json=payload, headers=headers)
        result = json.loads(response.text)
        answer = result['openai']['generated_text']
        speak(answer)
        return answer
    except Exception as e:
        error_msg = "Sorry, I couldn't connect to the AI service."
        speak(error_msg)
        return error_msg

# Time function
def time():
    t = datetime.now().strftime("%H:%M:%S")
    speak(f"Current time is {t}")
    return t

# Date function
def date():
    now = datetime.now()
    d = now.strftime("%d/%m/%Y")
    speak(f"Today's date is {d}")
    return d

# Screenshot function (disabled on Render due to no display)
def screenshot():
    if not os.getenv('RENDER'):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            img = ss.screenshot(filename)
            speak("Screenshot taken.")
            return filename
        except Exception as e:
            speak("Sorry, I couldn't take the screenshot.")
            return None
    else:
        speak("Screenshot feature is not available on this server.")
        return None

# Note-taking function
def take_note(note_content):
    db_path = os.path.join('/tmp', 'notes.db') if os.getenv('RENDER') else 'notes.db'
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO notes (content) VALUES (?)", (note_content,))
        conn.commit()
    speak("Note saved.")
    return "Note saved."

# Get all notes
def get_notes():
    db_path = os.path.join('/tmp', 'notes.db') if os.getenv('RENDER') else 'notes.db'
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT content, created_at FROM notes ORDER BY created_at DESC")
        return [{"content": row[0], "created_at": row[1]} for row in cursor]

# Weather function
def get_weather(city):
    try:
        api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        if not api_key:
            error_msg = "Weather API key is missing."
            speak(error_msg)
            return error_msg
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(weather_url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            weather_info = f"The weather in {city} is {desc} with a temperature of {temp} degrees Celsius."
            speak(weather_info)
            return weather_info
        else:
            error_msg = "Sorry, I couldn't fetch the weather information."
            speak(error_msg)
            return error_msg
    except:
        error_msg = "Sorry, I couldn't fetch the weather information."
        speak(error_msg)
        return error_msg

# Speech recognition (disabled on Render due to no microphone)
def takeCommand():
    if not os.getenv('RENDER'):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = r.listen(source, timeout=5)
                print("Recognizing...")
                query = r.recognize_google(audio, language='en-in')
                print(f"User said: {query}")
                return query.lower()
            except Exception as e:
                print(e)
                speak("Say that again please...")
                return "None"
    return "None"

# Process command
def process_command(query):
    if 'time' in query:
        return {"type": "time", "result": time()}
    elif 'date' in query:
        return {"type": "date", "result": date()}
    elif 'screenshot' in query:
        return {"type": "screenshot", "result": screenshot()}
    elif 'note' in query:
        note_content = re.sub(r'\b(take a note|note)\b', '', query, flags=re.IGNORECASE).strip()
        if note_content:
            return {"type": "note", "result": take_note(note_content)}
        return {"type": "error", "result": "Please provide note content."}
    elif 'weather' in query:
        city = re.sub(r'\b(weather in|weather)\b', '', query, flags=re.IGNORECASE).strip()
        if city:
            return {"type": "weather", "result": get_weather(city)}
        return {"type": "error", "result": "Please specify a city."}
    elif 'exit' in query:
        speak("Thank you for using me. Have a nice day!")
        return {"type": "exit", "result": "Exiting..."}
    else:
        return {"type": "ai", "result": talktoai(query)}

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def handle_command():
    query = request.json.get('command', '').lower()
    if query == 'get_notes':
        return jsonify({"type": "notes", "result": get_notes()})
    result = process_command(query)
    return jsonify(result)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
