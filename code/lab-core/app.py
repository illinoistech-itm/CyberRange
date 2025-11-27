from flask import Flask
from flask_socketio import SocketIO, emit
import websocket
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Connect to pyxtermjs backend WebSocket
def connect_pyxterm():
    ws = websocket.WebSocket()
    ws.connect("ws://localhost:5000/")  # pyxtermjs service
    return ws

# Keep a global reference for simplicity
pyxterm_ws = connect_pyxterm()

# Thread to read from pyxtermjs and forward to Socket.IO clients
def pyxterm_reader():
    while True:
        msg = pyxterm_ws.recv()
        socketio.emit("output", msg)

threading.Thread(target=pyxterm_reader, daemon=True).start()

# Handle client connect
@socketio.on("connect")
def handle_connect():
    print("Client connected")

# Handle input from client terminal
@socketio.on("input")
def handle_input(data):
    pyxterm_ws.send(data)
