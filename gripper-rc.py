import numpy as np
import pydantic
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import cv2
from cares_gripper.scripts.configurations import GripperConfig
from cares_gripper.scripts.Gripper import Gripper
import threading

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

camera = cv2.VideoCapture(0)

gripper_config = pydantic.parse_file_as(path="gripper_4DOF_config_ID1.json", type_=GripperConfig)
gripper = Gripper(gripper_config)

acceleration = 2

keys_pressed = set()
stream_quality = 0.25 # percentage
stream_running = False
servo_speeds = np.zeros(len(gripper_config.home_pose), dtype=int)
servo_positions = {}
new_positions = np.array(gripper.current_positions())

def process_movements():
    global gripper
    global servo_positions
    global new_positions
    while True:
            
        if len(servo_positions) > 0:
            new_positions = np.array(gripper.current_positions())
            for servo, value in servo_positions.items():
                new_positions[servo] = round((gripper_config.max_values[servo] - gripper_config.min_values[servo]) * value + gripper_config.min_values[servo])
            servo_positions = {}
                
        elif len(keys_pressed) > 0:
            new_positions = np.array(gripper.current_positions())
            if 'KeyJ' in keys_pressed and not 'KeyL' in keys_pressed:
                servo_speeds[0] += acceleration
            elif 'KeyL' in keys_pressed and not 'KeyJ' in keys_pressed:
                servo_speeds[0] -= acceleration
            else:
                servo_speeds[0] = 0


            if 'KeyK' in keys_pressed and not 'KeyI' in keys_pressed:
                servo_speeds[1] += acceleration
            elif 'KeyI' in keys_pressed and not 'KeyK' in keys_pressed:
                servo_speeds[1] -= acceleration
            else:
                servo_speeds[1] = 0

            if 'KeyS' in keys_pressed and not 'KeyF' in keys_pressed:
                servo_speeds[2] += acceleration
            elif 'KeyF' in keys_pressed and not 'KeyS' in keys_pressed:
                servo_speeds[2] -= acceleration
            else:
                servo_speeds[2] = 0

            if 'KeyE' in keys_pressed and not 'KeyD' in keys_pressed:
                servo_speeds[3] += acceleration
            elif 'KeyD' in keys_pressed and not 'KeyE' in keys_pressed:
                servo_speeds[3] -= acceleration
            else:
                servo_speeds[3] = 0

            new_positions = new_positions + servo_speeds

            if 'KeyH' in keys_pressed:
                new_positions = gripper_config.home_pose

            new_positions = np.clip(new_positions, gripper_config.min_values, gripper_config.max_values)

        else:
            servo_speeds = np.zeros(len(gripper_config.home_pose), dtype=int)
            continue
            
        try:
            gripper.move(new_positions)
        except:
            print("Gripper crashed.. reinitialize")
            gripper = Gripper(gripper_config)

def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            frame = cv2.resize(frame, (round(frame.shape[0] * stream_quality), round(frame.shape[1] * stream_quality)))
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield frame
        socketio.sleep(.05) # reduce network load

def stream_video():
    global new_positions
    for video_frame in gen_frames():
        tmp = new_positions[[3, 1, 2, 0]]
        tmp = (tmp - gripper_config.min_values) / (np.array(gripper_config.max_values) - np.array(gripper_config.min_values))
        tmp[2] = 1 - tmp[2]
        tmp[3] = 1 - tmp[3]
        socketio.emit('video_frame', {'data': video_frame, 'slider_values': tmp.tolist()})

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.event
def key_down(message):
    keys_pressed.add(message['key'])

@socketio.event
def key_up(message):
    keys_pressed.discard(message['key'])

@socketio.event
def adjust_stream_quality(message):
    global stream_quality
    stream_quality = float(message['value'])

@socketio.event
def set_servo_position(message):
    global servo_positions
    value = message['value']
    if message['servo'] == 0:
        servo_id = 3;
    elif message['servo'] == 1:
        servo_id = 1;
    elif message['servo'] == 2:
        servo_id = 2;
        value = 1 - value
    elif message['servo'] == 3:
        servo_id = 0;
        value = 1 - value

    servo_positions[servo_id] = value

@socketio.event
def ping():
    emit('pong')

@socketio.event
def connect():
    global stream_running
    if not stream_running:
        socketio.start_background_task(stream_video)
        stream_running = True
    emit('my_response', {'data': 'Connected', 'count': 0})


if __name__ == '__main__':
    movement_dispatcher = threading.Thread(target=process_movements)
    movement_dispatcher.start()
    socketio.run(app, allow_unsafe_werkzeug=True, debug=False, host="0.0.0.0")