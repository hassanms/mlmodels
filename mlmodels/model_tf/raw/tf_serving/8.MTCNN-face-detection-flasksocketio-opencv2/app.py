import base64
import io
import time
from os.path import abspath, dirname
from queue import Queue

import numpy as np

import cv2
from face_detection import detect_face
from flask import Flask, Response
from flask_socketio import SocketIO, emit, send
from PIL import Image

d = dirname(dirname(abspath(__file__)))

app = Flask(__name__)
app.queue = Queue()
socketio = SocketIO(app)


@socketio.on("connect", namespace="/live")
def test_connect():
    print("Client wants to connect.")
    emit("response", {"data": "OK"}, broadcast=True)


@socketio.on("disconnect", namespace="/live")
def test_disconnect():
    print("Client disconnected")


@socketio.on("event", namespace="/live")
def test_message(message):
    emit("response", {"data": message["data"]})
    print(message["data"])


@socketio.on("livevideo", namespace="/live")
def test_live(message):
    app.queue.put(message["data"])
    img_bytes = base64.b64decode(app.queue.get())
    img_np = np.array(Image.open(io.BytesIO(img_bytes)))
    img_np = detect_face(img_np)
    frame = cv2.imencode(".jpg", img_np)[1].tobytes()
    base64_bytes = base64.b64encode(frame)
    base64_string = base64_bytes.decode("utf-8")
    emit("camera_update", {"data": base64_string}, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="localhost", port=5000, debug=True)
