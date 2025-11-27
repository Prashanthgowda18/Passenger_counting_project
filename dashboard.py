from flask import Flask, render_template, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import json
import time
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC, CAPACITY_THRESHOLD

print("Starting dashboard app...")
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure key
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables to store current data
current_data = {
    'count_inside': 0,
    'total_entered': 0,
    'capacity': CAPACITY_THRESHOLD,
    'status': 'normal',
    'alerts': [],
    'timestamp': int(time.time())
}

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(MQTT_TOPIC)
    client.subscribe(f"{MQTT_TOPIC}/authorities")  # For authorities alerts

def on_message(client, userdata, msg):
    global current_data
    try:
        payload = json.loads(msg.payload.decode())

        if 'event' in payload:
            event = payload['event']
            if event == 'passenger_entered':
                current_data['total_entered'] = payload.get('total_entered', 0)
                current_data['count_inside'] = payload.get('total_entered', 0)
            elif event == 'bus_full':
                current_data['status'] = 'full'
        elif 'count' in payload:
            current_data['count_inside'] = payload['count']
            if current_data['count_inside'] == CAPACITY_THRESHOLD:
                current_data['status'] = 'full'
            else:
                current_data['status'] = 'normal'

        current_data['timestamp'] = payload.get('timestamp', int(time.time()))

        # Emit to all connected clients
        socketio.emit('update', current_data)

    except Exception as e:
        print(f"MQTT message error: {e}")

# Initialize MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    print("MQTT client connected and loop started")
except Exception as e:
    print(f"MQTT connection failed: {e}")

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', data=current_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    from flask import request
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Basic authentication with demo credentials
        if username == 'admin' and password == 'password':
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/extra-buses')
def extra_buses():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('extra_buses.html')

@app.route('/api/status')
def api_status():
    return jsonify(current_data)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('update', current_data)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)