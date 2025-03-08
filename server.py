import sys
import os
import ctypes
import time
import threading
import json
from flask import Flask, redirect, jsonify
import pystray
from pystray import MenuItem as item, Icon
from PIL import Image

app = Flask(__name__)

DATA_FILE = "url_mapping.json"

# Function to load stored URLs
def load_urls():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Route to handle shortened URL redirects
@app.route('/<alias>')
def redirect_to_original(alias):
    urls = load_urls()
    if alias in urls:
        return redirect(urls[alias]["original"], code=302)
    return jsonify({"error": "Shortened URL not found"}), 404

# Function to toggle console visibility
def toggle_console(icon, item):
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        is_visible = ctypes.windll.user32.IsWindowVisible(hwnd)
        ctypes.windll.user32.ShowWindow(hwnd, 0 if is_visible else 1)

# Function to start Flask server
def run_server():
    app.run(host='0.0.0.0', port=5000)

# Function to fully exit the program
def exit_app(icon, item):
    icon.stop()
    os._exit(0)  # Force exit

# Auto-hide console at launch
hwnd = ctypes.windll.kernel32.GetConsoleWindow()
if hwnd:
    ctypes.windll.user32.ShowWindow(hwnd, 0)  # 0 = Hide, 1 = Show

# Load the tray icon from the specified path
tray_icon_path = "C:\\ProgramData\\Microsoft\\User Account Pictures\\user.png"
try:
    tray_icon_image = Image.open(tray_icon_path)
except Exception as e:
    print(f"Error loading image: {e}")
    tray_icon_image = Image.new('RGB', (64, 64), (255, 255, 255))  # Fallback to blank image

# Load the tray icon
tray_icon = Icon("URL Shortener", tray_icon_image, menu=(item('Show/Hide Console', toggle_console), item('Exit', exit_app)))

# Start Flask server in a separate thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Start system tray icon
tray_icon.run()
