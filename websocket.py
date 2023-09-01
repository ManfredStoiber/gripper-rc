import numpy as np
import pydantic
from flask import Flask, render_template, request, copy_current_request_context, Response
from flask_socketio import SocketIO, emit, disconnect
import cv2
from cares_gripper.scripts.configurations import GripperConfig
from cares_gripper.scripts.Gripper import Gripper
import threading
import time

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

camera = cv2.VideoCapture(0)

keys_pressed = set()

gripper_config = pydantic.parse_file_as(path="gripper_4DOF_config_ID1.json", type_=GripperConfig)
gripper = Gripper(gripper_config)

def process_movements():
    while True:
        positions = gripper.current_positions()
        if 'KeyJ' in keys_pressed:
            positions[0] += 10
        if 'KeyL' in keys_pressed:
            positions[0] -= 10

        if 'KeyK' in keys_pressed:
            positions[1] += 10
        if 'KeyI' in keys_pressed:
            positions[1] -= 10

        if 'KeyS' in keys_pressed:
            positions[2] += 10
        if 'KeyF' in keys_pressed:
            positions[2] -= 10

        if 'KeyE' in keys_pressed:
            positions[3] += 10
        if 'KeyD' in keys_pressed:
            positions[3] -= 10

        positions = np.clip(positions, gripper_config.min_values, gripper_config.max_values)
        gripper.move(positions)
        gripper.step()
        time.sleep(2)


def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            #frame = cv2.resize(frame, (64, 64))
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield frame
            #yield (b'--frame\r\n'
            #       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
        socketio.sleep(0)
        print("Frame")

def stream_video():
    for video_frame in gen_frames():
        socketio.emit('my_video_frame', {'data': video_frame})

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.event
def key_down(message):
    keys_pressed.add(message['key'])
    #emit('my_response',
    #     {'data': str(keys_pressed)})

@socketio.event
def key_up(message):
    keys_pressed.remove(message['key'])
    #emit('my_response',
    #     {'data': str(keys_pressed)})

@socketio.event
def my_event(message):
    emit('my_response',
         {'data': message['data']})

@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!'},
         callback=can_disconnect)


@socketio.event
def my_ping():
    print("Ping, send Pong")
    emit('my_pong')


@socketio.event
def connect():
    socketio.start_background_task(stream_video)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    movement_dispatcher = threading.Thread(target=process_movements)
    movement_dispatcher.start()
    socketio.run(app, allow_unsafe_werkzeug=True, debug=False, host="0.0.0.0")
