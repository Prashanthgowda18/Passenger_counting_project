import cv2
import time
import numpy as np
from detector import Detector
from tracker import CentroidTracker
import paho.mqtt.client as mqtt
from config import *
import json


# Safety (simulate hardware)
def door_alert():
    print("[SAFETY] Door alert sound triggered!")
    print(f"Dashboard link: {DASHBOARD_LINK}")

def engine_stop():
    print("[SAFETY] Engine stop triggered!")

# Beginner-friendly helper to notify authorities via MQTT
# - Keeps all authority alerts in one place
def notify_authorities(client, event, message, extra=None):
    if client is None:
        # Silent skip for authorities notification when no MQTT client
        return
    payload = {
        "event": event,
        "message": message,
        "timestamp": int(time.time())
    }
    if extra:
        payload.update(extra)
    try:
        client.publish(MQTT_TOPIC_AUTHORITIES, json.dumps(payload), qos=1, retain=False)
        # Silent success for authorities notification
    except Exception as e:
        # Silent error handling for authorities notification
        pass

def main():
    print(f"Dashboard link: {DASHBOARD_LINK}")
    # Initialize detector and tracker with improved parameters
    det = Detector(MODEL_PATH, conf=CONFIDENCE)
    tracker = CentroidTracker(maxDisappeared=60, maxDistance=80)

    cap = cv2.VideoCapture(VIDEO_SOURCE)
    if not cap.isOpened():
        print("Error opening video source:", VIDEO_SOURCE)
        return

    # MQTT setup
    client = mqtt.Client()
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print("MQTT connect failed:", e)
        client = None

    last_publish = time.time()
    count_inside = 0
    counted_ids = set()
    total_entered = 0  # Track total passengers who entered
    passenger_counter = 0  # Sequential passenger counter
    bus_full_alert_sent = False  # Ensure we alert only once per run
    door_close_alert_sent = False  # Ensure door close alert only once

    # Read first frame to compute line position
    ret, frame = cap.read()
    if not ret:
        print("Cannot read from source")
        return
    H, W = frame.shape[:2]
    line_x = int(W * LINE_POSITION)  # Vertical line on right side

    print("Starting loop. Press 'q' to quit.")
    print(f"Dashboard link: {DASHBOARD_LINK}")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect people
        dets = det.detect(frame)
        rects = [(x1, y1, x2, y2) for (x1, y1, x2, y2, conf, cls) in dets]

        # Update tracker
        objects = tracker.update(rects)

        # Draw vertical counting line on right side (smaller line)
        cv2.line(frame, (line_x, 0), (line_x, H), (0, 255, 255), 1)

        # Loop over tracked objects
        for objectID, tobj in list(objects.items()):
            cX, cY = tobj.centroid
            x1, y1, x2, y2 = tobj.bbox

            # Check for right-side movement
            moved_right = tracker.check_right_movement(objectID, W)
            if moved_right:
                tobj.moved_right = True

            # Draw bounding box & ID with single color
            color = (255, 255, 255)  # White for all

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            # Show passenger number only if they entered
            if tobj.entered and tobj.passenger_number > 0:
                cv2.putText(frame, f"P{tobj.passenger_number}", (x1, y1 - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

            # Detect crossing events with improved logic and movement validation
            if len(tobj.history) >= 2:  # Reduced requirement for faster detection
                # Get recent positions for validation
                prev_x = tobj.history[-2][0]  # X coordinate for vertical line
                curr_x = tobj.history[-1][0]
                
                # Calculate movement for validation
                movement = abs(curr_x - prev_x)

                # Crossing from left to right → entering (more sensitive detection)
                if (prev_x < line_x and curr_x >= line_x and 
                    not tobj.entered and movement >= MIN_MOVEMENT_PIXELS):
                    tobj.entered = True
                    count_inside += 1
                    total_entered += 1
                    passenger_counter += 1
                    tobj.passenger_number = passenger_counter
                    print(f"Passenger {passenger_counter} ENTERED. Total Entered: {total_entered}")
                    # Send immediate MQTT alert with QoS 1
                    if client:
                        alert_payload = {
                            "event": "passenger_entered",
                            "total_entered": total_entered,
                            "timestamp": int(time.time())
                        }
                        try:
                            client.publish(MQTT_TOPIC, json.dumps(alert_payload), qos=1, retain=False)
                        except Exception as e:
                            print("MQTT alert publish failed:", e)

                # No exit detection - only entry detection

        # Display only total entered count
        cv2.putText(frame, f"Total Entered: {total_entered}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        # Detection line is drawn but no text labels

        # Safety check - Request extra bus when passenger count is low (<= 10)
        if count_inside <= 10 and count_inside > 0:
            if not bus_full_alert_sent:
                if client:
                    try:
                        payload_bus_full = json.dumps({
                            "event": "bus_full",
                            "message": "Passenger count is low, allocate extra bus for better distribution",
                            "count_inside": count_inside,
                            "timestamp": int(time.time())
                        })
                        client.publish(MQTT_TOPIC, payload_bus_full, qos=1, retain=False)
                    except Exception as e:
                        print("MQTT bus-full publish failed:", e)
                # Always notify authorities (even if public topic failed)
                notify_authorities(
                    client,
                    event="bus_full",
                    message="Passenger count is low, allocate extra bus for better distribution",
                    extra={"count_inside": count_inside}
                )
                bus_full_alert_sent = True

        if total_entered >= DOOR_CLOSE_THRESHOLD and not door_close_alert_sent:
            print("[ALERT] door close")
            door_alert()
            if client:
                try:
                    payload_door_close = json.dumps({
                        "event": "door_close",
                        "message": "door close",
                        "threshold": DOOR_CLOSE_THRESHOLD,
                        "total_entered": total_entered,
                        "count_inside": count_inside,
                        "timestamp": int(time.time())
                    })
                    client.publish(MQTT_TOPIC, payload_door_close, qos=1, retain=False)
                except Exception as e:
                    print("MQTT door-close publish failed:", e)
            door_close_alert_sent = True

        # Display the frame
        cv2.imshow("Passenger Counter", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        # MQTT Publish
        if client and (time.time() - last_publish) > PUBLISH_INTERVAL_SEC:
            payload = {"count": count_inside, "timestamp": int(time.time())}
            try:
                client.publish(MQTT_TOPIC, json.dumps(payload), qos=1, retain=False)
            except Exception as e:
                print("MQTT publish failed:", e)
            last_publish = time.time()

    cap.release()
    cv2.destroyAllWindows()
    if client:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
