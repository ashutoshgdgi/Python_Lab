"""
STAR - A JARVIS-style personal AI assistant

Install:
    pip install pyttsx3 SpeechRecognition pyaudio pyautogui psutil anthropic requests

Optional AI brain (answers any question, understands natural language):
    set ANTHROPIC_API_KEY=your_key      (Windows)
    export ANTHROPIC_API_KEY=your_key   (Mac/Linux)

Run:
    python star.py            -> voice mode (falls back to text if no mic)
    python star.py --text     -> text mode
"""

import os
import sys
import json
import time
import shutil
import platform
import subprocess
import webbrowser
import datetime
from pathlib import Path

import pyttsx3
import psutil
import pyautogui

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import anthropic
except ImportError:
    anthropic = None

NAME = "Star"
OS = platform.system()  # Windows / Darwin / Linux
MODEL = os.getenv("STAR_MODEL", "claude-sonnet-5-5")

# ---------------------------------------------------------------- voice out
engine = pyttsx3.init()
engine.setProperty("rate", 175)
voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)


def say(text: str):
    print(f"{NAME}: {text}")
    engine.say(text)
    engine.runAndWait()


# ---------------------------------------------------------------- voice in
recognizer = sr.Recognizer() if sr else None


def listen(voice_mode: bool) -> str:
    if not voice_mode:
        return input("You: ").strip().lower()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.4)
            print("Listening...")
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=12)
        text = recognizer.recognize_google(audio).lower()
        print(f"You: {text}")
        return text
    except Exception:
        return ""


def confirm(question: str, voice_mode: bool) -> bool:
    """Ask before doing anything destructive."""
    say(question + " Say yes or no.")
    return listen(voice_mode) in ("yes", "yeah", "yep", "confirm", "do it", "y")


# ---------------------------------------------------------------- AI brain
history = []


def ask_ai(prompt: str) -> str:
    if not anthropic or not os.getenv("ANTHROPIC_API_KEY"):
        return ("My AI brain is offline. Set the ANTHROPIC_API_KEY environment "
                "variable to let me answer general questions.")
    client = anthropic.Anthropic()
    history.append({"role": "user", "content": prompt})
    reply = client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=(f"You are {NAME}, a witty, loyal, concise voice assistant like JARVIS. "
                "Reply in 1-3 short spoken-style sentences. No markdown."),
        messages=history[-12:],
    )
    text = reply.content[0].text
    history.append({"role": "assistant", "content": text})
    return text


# ---------------------------------------------------------------- actions
APPS = {
    "Windows": {
        "notepad": "notepad", "calculator": "calc", "chrome": "start chrome",
        "paint": "mspaint", "explorer": "explorer", "cmd": "start cmd",
        "vs code": "code", "word": "start winword", "excel": "start excel",
        "spotify": "start spotify",
    },
    "Darwin": {
        "notepad": "open -a TextEdit", "calculator": "open -a Calculator",
        "chrome": "open -a 'Google Chrome'", "safari": "open -a Safari",
        "terminal": "open -a Terminal", "vs code": "open -a 'Visual Studio Code'",
        "spotify": "open -a Spotify",
    },
    "Linux": {
        "calculator": "gnome-calculator", "chrome": "google-chrome",
        "terminal": "gnome-terminal", "vs code": "code", "files": "nautilus",
    },
}


def open_app(name: str) -> str:
    cmd = APPS.get(OS, {}).get(name)
    if cmd:
        subprocess.Popen(cmd, shell=True)
        return f"Opening {name}."
    # fall back: try running the name directly
    if shutil.which(name):
        subprocess.Popen(name, shell=True)
        return f"Opening {name}."
    return f"I don't know how to open {name} yet."


def set_volume(direction: str):
    key = {"up": "volumeup", "down": "volumedown", "mute": "volumemute"}[direction]
    for _ in range(5 if direction != "mute" else 1):
        pyautogui.press(key)


def screenshot() -> str:
    path = Path.home() / "Pictures" / f"star_{int(time.time())}.png"
    path.parent.mkdir(exist_ok=True)
    pyautogui.screenshot(str(path))
    return f"Screenshot saved to {path}."


def system_status() -> str:
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    bat = psutil.sensors_battery()
    out = f"CPU is at {cpu} percent, memory at {ram} percent."
    if bat:
        out += f" Battery is {int(bat.percent)} percent."
    return out


def power(action: str):
    cmds = {
        "Windows": {"shutdown": "shutdown /s /t 5", "restart": "shutdown /r /t 5",
                    "lock": "rundll32.exe user32.dll,LockWorkStation",
                    "sleep": "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"},
        "Darwin": {"shutdown": "osascript -e 'tell app \"System Events\" to shut down'",
                   "restart": "osascript -e 'tell app \"System Events\" to restart'",
                   "lock": "pmset displaysleepnow", "sleep": "pmset sleepnow"},
        "Linux": {"shutdown": "shutdown now", "restart": "reboot",
                  "lock": "loginctl lock-session", "sleep": "systemctl suspend"},
    }
    os.system(cmds[OS][action])


def find_file(name: str) -> str:
    for root in (Path.home() / "Documents", Path.home() / "Desktop", Path.home() / "Downloads"):
        for p in root.rglob(f"*{name}*"):
            if p.is_file():
                if OS == "Windows":
                    os.startfile(p)
                else:
                    subprocess.Popen(["open" if OS == "Darwin" else "xdg-open", str(p)])
                return f"Opening {p.name}."
    return f"I couldn't find a file called {name}."


def run_shell(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    out = (result.stdout or result.stderr).strip()
    return out[:300] if out else "Command finished with no output."


# ---------------------------------------------------------------- brain / router
def handle(cmd: str, voice_mode: bool) -> bool:
    """Returns False when Star should shut down."""
    if not cmd:
        return True

    if any(w in cmd for w in ("goodbye", "exit", "quit", "go to sleep star", "stop listening")):
        say("Goodbye. Star powering down.")
        return False

    if cmd.startswith(("open ", "launch ", "start ")):
        target = cmd.split(" ", 1)[1].strip()
        say(open_app(target))

    elif "time" in cmd and "what" in cmd:
        say(datetime.datetime.now().strftime("It's %I:%M %p."))

    elif "date" in cmd or "today" in cmd and "day" in cmd:
        say(datetime.datetime.now().strftime("Today is %A, %B %d, %Y."))

    elif cmd.startswith(("search ", "google ")):
        q = cmd.split(" ", 1)[1]
        webbrowser.open(f"https://www.google.com/search?q={q.replace(' ', '+')}")
        say(f"Searching for {q}.")

    elif cmd.startswith("play "):
        q = cmd[5:].replace("on youtube", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}")
        say(f"Playing {q} on YouTube.")

    elif "go to " in cmd and "." in cmd:
        site = cmd.split("go to ", 1)[1].replace(" dot ", ".").replace(" ", "")
        webbrowser.open(site if site.startswith("http") else f"https://{site}")
        say(f"Opening {site}.")

    elif "volume up" in cmd:
        set_volume("up"); say("Volume up.")
    elif "volume down" in cmd:
        set_volume("down"); say("Volume down.")
    elif "mute" in cmd:
        set_volume("mute"); say("Muted.")

    elif "screenshot" in cmd:
        say(screenshot())

    elif "system status" in cmd or "how is my computer" in cmd:
        say(system_status())

    elif cmd.startswith("find file ") or cmd.startswith("open file "):
        say(find_file(cmd.split("file ", 1)[1]))

    elif cmd.startswith("type "):
        time.sleep(1.5)
        pyautogui.write(cmd[5:], interval=0.03)

    elif cmd.startswith("run command "):
        shell = cmd[len("run command "):]
        if confirm(f"Run the command {shell}?", voice_mode):
            try:
                say(run_shell(shell))
            except Exception as e:
                say(f"That failed: {e}")
        else:
            say("Cancelled.")

    elif cmd in ("lock computer", "lock the computer"):
        power("lock")
    elif "sleep computer" in cmd:
        power("sleep")
    elif "shut down" in cmd or "shutdown" in cmd:
        if confirm("Are you sure you want to shut down the computer?", voice_mode):
            say("Shutting down."); power("shutdown")
    elif "restart computer" in cmd or "reboot" in cmd:
        if confirm("Are you sure you want to restart?", voice_mode):
            say("Restarting."); power("restart")

    else:
        say(ask_ai(cmd))

    return True


# ---------------------------------------------------------------- main loop
def main():
    voice_mode = "--text" not in sys.argv and sr is not None
    hour = datetime.datetime.now().hour
    greet = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    say(f"{greet}. {NAME} online and ready.")

    running = True
    while running:
        if voice_mode:
            heard = listen(True)
            if NAME.lower() not in heard:       # wake word
                continue
            cmd = heard.split(NAME.lower(), 1)[1].strip()
            if not cmd:
                say("Yes?")
                cmd = listen(True)
        else:
            cmd = listen(False)
            cmd = cmd.replace(NAME.lower(), "", 1).strip(" ,")
        running = handle(cmd, voice_mode)


if __name__ == "__main__":
    main()