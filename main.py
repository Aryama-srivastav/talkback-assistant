import sqlite3 
import pyttsx3
import speech_recognition as sr
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from threading import Thread
import sys
import datetime
import os
import wikipedia
import pyjokes
import difflib
import random

con = sqlite3.connect("dbase.db")
cur = con.cursor()

speaker = pyttsx3.init()
speaker.setProperty('volume', 1.0)
speaker.setProperty('rate', 120)
speaker.setProperty('voice', speaker.getProperty('voices')[0].id)
listener = sr.Recognizer()

root = tk.Tk()
root.title("Ary Talk-Back Assistant")
root.geometry("400x400")
root.resizable(False, False)

gif_label = tk.Label(root)
gif_label.pack(expand=True)

continue_animation = [False]

def show_default():
    if os.path.exists("default.png"):
        img = ImageTk.PhotoImage(Image.open("default.png"))
        gif_label.config(image=img)
        gif_label.image = img

show_default()

def show_gif(path, duration=5000, fallback_image="default.png"):
    try:
        sequence = [ImageTk.PhotoImage(img.copy()) for img in ImageSequence.Iterator(Image.open(path))]
        frame_count = len(sequence)

        def animate(counter=0):
            gif_label.config(image=sequence[counter])
            gif_label.image = sequence[counter]
            counter = (counter + 1) % frame_count
            if continue_animation[0]:
                root.after(100, animate, counter)

        continue_animation[0] = True
        animate()

        def stop_animation():
            continue_animation[0] = False
            show_default()

        root.after(duration, stop_animation)
    except Exception as e:
        print(f"Error displaying GIF: {e}")

def talk(text):
    print("Ary:", text)
    speaker.say(text)
    speaker.runAndWait()

def take_command():
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source, duration=0.2)
            print("🎧 Listening...")
            audio = listener.listen(source, timeout=4, phrase_time_limit=5)
            command = listener.recognize_google(audio).lower()
            print("You said:", command)
            return command
    except:
        return "False"

def insertdata(person):
    try:
        with sr.Microphone() as source:
            show_gif('speak.gif', 8000)
            talk(f"Please tell something about {person}")
            audio = listener.listen(source, timeout=4, phrase_time_limit=5)
            info = listener.recognize_google(audio)
            cur.execute("INSERT OR REPLACE INTO data (name, about) VALUES (?, ?)", (person, info))
            con.commit()
            show_gif('speak.gif', 8000)
            talk(f"Got it! Saved information about {person}.")
    except Exception as e:
        print("Error:", e)
        show_gif('speak.gif', 8000)
        talk("Sorry, I couldn't save that.")

def fetch_about(person):
    cur.execute("SELECT about FROM data WHERE LOWER(name) = LOWER(?)", (person,))
    result = cur.fetchone()
    if result:
        return result[0]

    cur.execute("SELECT name FROM data")
    all_names = [row[0] for row in cur.fetchall()]
    matches = difflib.get_close_matches(person, all_names, n=1, cutoff=0.6)
    if matches:
        matched_name = matches[0]
        cur.execute("SELECT about FROM data WHERE name = ?", (matched_name,))
        result = cur.fetchone()
        if result:
            show_gif('speak.gif', 8000)
            talk(f"I guessed you meant {matched_name}.")
            return result[0]
    return None

fail_count = 0
listening_active = [True]
compliments = ["good", "awesome", "great job", "well done", "smart", "cool"]

def run_ary():
    global fail_count
    while listening_active[0]:
        command = take_command()
        if not command or command == "False":
            fail_count += 1
            if fail_count >= 2:
                show_gif('bye.gif', 8000)
                talk("Looks like you're away. Signing off...")
                root.quit()
                break
            show_gif('speak.gif', 8000)
            talk("Didn't catch that. Try again or say 'ok bye' to exit.")
            continue
        else:
            fail_count = 0

        if 'who is' in command:
            person = command.replace('who is', '').strip()
            about_info = fetch_about(person)
            if about_info:
                show_gif('speak.gif', 8000)
                talk(about_info)
            else:
                show_gif('speak.gif', 8000)
                talk(f"Sorry, I don't know who {person} is. Can you tell me?")
                insertdata(person)

        elif 'time' in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            show_gif('speak.gif', 8000)
            talk("The current time is " + time)

        elif 'yourself' in command:
            show_gif('speak.gif', 8000)
            talk("I am Ary, a talk-back assistant created by Aryama Srivastav.")

        elif any(x in command for x in ['ok bye', 'abort', 'shut up']):
            show_gif('bye.gif', 8000)
            talk("Okay, goodbye!")
            root.quit()
            break

        elif 'how are you' in command:
            show_gif('speak.gif', 8000)
            talk("I'm feeling electric! How about you?")

        elif 'i love you' in command or 'i like you' in command:
            show_gif('speak.gif', 8000)
            talk("Aww, thank you! I love knowledge and people who seek it!")

        elif 'are you real' in command:
            show_gif('speak.gif', 8000)
            talk("I'm as real as the code that runs me. Pretty deep, huh?")

        elif 'fact' in command:
            show_gif('speak.gif', 8000)
            summary = wikipedia.summary("random", sentences=1)
            talk("Here's a fact: " + summary)

        elif 'joke' in command:
            show_gif('speak.gif', 8000)
            joke = pyjokes.get_joke()
            talk(joke)

        elif any(phrase in command for phrase in compliments):
            replies = [
                "Aww, thank you! I try my best.",
                "You're making me blush... if I could blush!",
                "You're sweet! Thanks a ton!",
                "I live to assist. You're awesome too!"]
            show_gif('speak.gif', 8000)
            talk(random.choice(replies))

        elif "story" in command:
            speaker.setProperty('volume', 0.1)
            speaker.setProperty('rate', 100)
            show_gif('speak.gif', 8000)
            talk("Once upon a time, in a land far away...")
            speaker.setProperty('volume', 0.2)
            talk("Would you like to turn left or right?")
            speaker.setProperty('volume', 1.0)
            speaker.setProperty('rate', 120)
            talk("Haha! Just kidding. Go straight to Kindle and grab a real adventure!")

        elif "music" in command or "sing" in command:
            show_gif('speak.gif', 8000)
            talk("Well... won't you mind listening to me sing?")
            talk("Just kidding! Head over to Spotify for the real beat.")

        elif any(word in command for word in ["luck", "horoscope", "future", "prediction"]):
            speaker.setProperty('volume', 0.1)
            speaker.setProperty('rate', 100)
            show_gif('speak.gif', 8000)
            talk("You know my secret...")
            speaker.setProperty('volume', 1.0)
            speaker.setProperty('rate', 120)
            talk("Go to astrowrit.com and you will be amazed.")

        elif any(word in command for word in ["bye", "abort", "shut up", "stop it", "quit", "exit"]):
            byes = [
                "Bye for now! Go be awesome like always!",
                "See you soon! Don’t miss me too much!",
                "Okay, logging out. But if you need me, you know where to find me!",
                "Goodbye! Don’t forget, I’m always a call away — just say Ary!"]
            show_gif('bye.gif', 8000)
            talk(random.choice(byes))
            root.quit()
            break

        else:
            show_gif('speak.gif', 6000)
            talk("Say that again...")

def start_ary_thread():
    Thread(target=run_ary, daemon=True).start()

def stop_ary():
    listening_active[0] = False
    show_gif('bye.gif', 8000)
    talk(" Bye for now!")
    root.quit()

start_button = tk.Button(root, text="Start Ary", command=start_ary_thread)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Ary", command=stop_ary)
stop_button.pack(pady=10)

def greet_user():
    greetings = [
        "Yo! Ary is online",
        "Wassup? I'm here to help you out!",
        "Ary booted and charged!",
        "Welcome back! I am listening"]
    show_gif('hi.gif', 8000)
    talk(random.choice(greetings))

greet_user()
root.mainloop()
