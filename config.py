# Video input
VIDEO_SOURCE = "passenger_video.mp4"

# YOLO model
MODEL_PATH = "yolov8n.pt"  # lightweight YOLOv8
CONFIDENCE = 0.3  # Lower confidence for better detection

# Counting line (relative position) - NOW ON RIGHT SIDE
LINE_POSITION = 0.8  # right side of frame (0 = left, 1 = right)
DIRECTION_TOLERANCE = 10  # pixel tolerance for direction
RIGHT_SIDE_THRESHOLD = 0.6  # threshold for right side movement (0.6 = 60% from left)

# Movement validation - IMPROVED FOR BETTER ACCURACY
MIN_MOVEMENT_PIXELS = 10  # minimum pixels moved to count as valid movement
MOVEMENT_HISTORY_FRAMES = 3  # frames to track for movement validation

# Overcrowding threshold
CAPACITY_THRESHOLD = 10  # Bus capacity is 10 passengers
DOOR_CLOSE_THRESHOLD = 10  # trigger door close alert above this count

# MQTT settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "transport/bus1/passenger_count"
MQTT_TOPIC_AUTHORITIES = "transport/bus1/authorities"  # alerts to authorities

# Hardware safety pins (if used)
USE_GPIO = False
DOOR_ALERT_PIN = 17
ENGINE_STOP_PIN = 27

# Publishing interval
PUBLISH_INTERVAL_SEC = 5

# Dashboard URL
DASHBOARD_LINK = "http://127.0.0.1:5000/"
