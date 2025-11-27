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
**Important: You must run both scripts simultaneously in separate terminals for the dashboard to work.**

1. **Terminal 1: Start the dashboard server** (this will also listen to MQTT topics and emit updates to connected clients):
	```powershell
	python dashboard.py
	```
	The dashboard will be available at `http://127.0.0.1:5000/`. Keep this terminal running.

2. **Terminal 2: Start the main video processing** (counts, MQTT publishing):
	```powershell
	python main.py
	```
	This will start the passenger counting and display terminal output. Keep this terminal running.

3. **Access the dashboard:**
	- Open your browser and go to: `http://127.0.0.1:5000/`
	- Login using the demo credentials:
	  - Username: `admin`
	  - Password: `admin123`

**Troubleshooting Dashboard Access:**
- If you get "ERR_CONNECTION_REFUSED", it means the dashboard server isn't running
- Make sure `python dashboard.py` is running in one terminal
- The dashboard server must stay running for the web interface to work

When the system publishes MQTT messages (to `MQTT_TOPIC`), the dashboard subscribes and updates in real time.

## Notes & Tips
- Alerts shown on the dashboard are now scoped to extra-bus allocations and full-bus events. Door-close alerts were removed by default.
- To change the logout placement or styling, edit `templates/dashboard.html`'s CSS section (the logout button is in the top-right corner).
- To push to GitHub: create a repo on GitHub and follow the `git remote add` / `git push` steps.

## Known Limitations
### Dashboard Access Issue
When `main.py` is executed from the terminal, the application successfully starts and prints the dashboard URL (for example, http://127.0.0.1:5000/). However, the dashboard does not always open correctly in the Chrome browser and often shows a "This site can't be reached" or similar error. This issue is likely related to the local server not binding properly to the port, the process stopping unexpectedly, or a browser/port conflict. Due to time constraints, this bug was not fully resolved, so the dashboard access may fail intermittently.

**Quick checklist (why Chrome shows error):**
- **Is the server actually running?** After running `python dashboard.py` first, then `python main.py`, the terminal should keep running (not exit with an error).
- **Check the URL carefully:** Make sure it's exactly like `http://127.0.0.1:5000/` or `http://localhost:5000/`. Don't miss the `http://`.
- **Port already in use:** Sometimes another app is using that port. Try changing the port in your code, e.g., for Flask: `app.run(host="0.0.0.0", port=5001, debug=True)`.
- **Firewall / antivirus / VPN:** Sometimes they block local ports.

## Troubleshooting
- If the dashboard doesn't update, ensure your MQTT broker is running and that `MQTT_BROKER`/`MQTT_PORT` in `config.py` are correct.
- If the YOLO model fails to load, confirm the `yolov8n.pt` file exists in the project root and that the ultralytics runtime is installed.

## License
This project is provided as-is for demo/learning purposes. Update the license as needed.

