# Passenger Counting Project

Lightweight bus passenger counting system with a real-time web dashboard and MQTT integration. The project uses a YOLO model for person detection, a centroid tracker for object tracking, and a Flask + Socket.IO dashboard for live updates.

## Features
- Real-time passenger counting from a video source (file or camera)
- YOLOv8-based person detection (lightweight `yolov8n.pt` included)
- Centroid tracking to maintain identities and validate movement
- MQTT publishing for external integrations and authority alerts
- Flask + Socket.IO dashboard for live counts, capacity status and manual allocation of standby buses
- Simple login (demo credentials) and logout flow

## Repo structure
- `main.py` — video processing loop, detection, tracking, and MQTT publishing
- `dashboard.py` — Flask + Socket.IO server that subscribes to MQTT and serves the dashboard
- `config.py` — configuration (video source, MQTT, thresholds, etc.)
- `templates/` — HTML templates (`dashboard.html`, `login.html`)
- `detector.py`, `tracker.py` — detection and tracking utilities
- `yolov8n.pt` — model file (lightweight YOLOv8)
- `requirements.txt` — Python dependencies

## Requirements
- Python 3.8+
- See `requirements.txt` for required packages (Flask, flask-socketio, paho-mqtt, ultralytics/YOLO runtime, etc.)

## Setup (local)
1. Clone or copy the repository to your machine.
2. Create and activate a virtual environment (Windows PowerShell):
	```powershell
	python -m venv .venv
	.\.venv\Scripts\Activate.ps1
	```
3. Install dependencies:
	```powershell
	pip install -r requirements.txt
	```
4. (Optional) If you plan to use GPU features of the YOLO model, follow the ultralytics/YOLO installation notes for CUDA support.

## Configuration
Edit `config.py` to set:
- `VIDEO_SOURCE` — path to video file or camera index
- `MQTT_BROKER`, `MQTT_PORT`, `MQTT_TOPIC` — MQTT connection settings
- `CAPACITY_THRESHOLD` — bus capacity threshold

There are a few optional runtime flags inside `templates/dashboard.html` (e.g. `DEBUG_SIMULATION`) for demo data.

## Running the system
1. Start the dashboard server (this will also listen to MQTT topics and emit updates to connected clients):
	```powershell
	python dashboard.py
	```
	The dashboard will be available at `http://localhost:5000/`.

2. Start the main video processing (counts, MQTT publishing):
	```powershell
	python main.py
	```

3. Login to the dashboard using the demo credentials:
	- Username: `admin`
	- Password: `admin123`

When the system publishes MQTT messages (to `MQTT_TOPIC`), the dashboard subscribes and updates in real time.

## Notes & Tips
- Alerts shown on the dashboard are now scoped to extra-bus allocations and full-bus events. Door-close alerts were removed by default.
- To change the logout placement or styling, edit `templates/dashboard.html`'s CSS section (the logout button is in the top-right corner).
- To push to GitHub: create a repo on GitHub and follow the `git remote add` / `git push` steps.

## Troubleshooting
- If the dashboard doesn't update, ensure your MQTT broker is running and that `MQTT_BROKER`/`MQTT_PORT` in `config.py` are correct.
- If the YOLO model fails to load, confirm the `yolov8n.pt` file exists in the project root and that the ultralytics runtime is installed.

## License
This project is provided as-is for demo/learning purposes. Update the license as needed.

---
If you'd like, I can add a short section with deployment steps (Docker / systemd) or a CONTRIBUTING guide.