from flask import Flask
from flask_socketio import SocketIO, emit
import socketio

app = Flask(__name__)
flask_sio = SocketIO(app, cors_allowed_origins="*")

# Connect to pyxtermjs backend (running on localhost:5000 for example)
backend_sio = socketio.Client()
backend_sio.connect("ws://127.0.0.1:5000")

@app.route("/")
def index():
    return "Socket.IO HTTPS → WSS bridge"

@flask_sio.on("input")
def handle_input(data):
    # Forward input to pyxtermjs
    backend_sio.emit("input", data)

@backend_sio.on("output")
def handle_output(data):
    # Forward backend output to client
    socketio.emit("output", data)
    