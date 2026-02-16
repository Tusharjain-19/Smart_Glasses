# 📱 Mobile Web App Guide

Complete guide to using the Smart Glasses mobile control panel.

---

## 🌐 Accessing the Web App

### On Your Phone (Same WiFi as Raspberry Pi)

**Option 1: Using Hostname (Easiest)**
```
http://raspberrypi.local:5000
```

**Option 2: Using IP Address**
```
http://192.168.1.xxx:5000
```

To find your Pi's IP address:
```bash
# On the Pi:
hostname -I

# Output: 192.168.1.42
# Then open: http://192.168.1.42:5000
```

**Option 3: Using Pi's Hotspot (No WiFi Required)**

Setup Pi as WiFi hotspot:
```bash
sudo nmcli device wifi hotspot ssid SmartGlasses password smartglasses123
```

Then connect phone to "SmartGlasses" network and open:
```
http://10.42.0.1:5000
```

---

## 🚀 Starting the Web App

### Method 1: Manual Start

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Navigate to project
cd ~/Smart_Glasses

# Activate virtual environment
source venv/bin/activate

# Start web app
python webapp/app.py
```

**Output:**
```
=== Smart Glasses Web App ===
Starting server on http://0.0.0.0:5000
Access from your phone: http://<pi-ip-address>:5000
Or: http://raspberrypi.local:5000
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.42:5000
```

### Method 2: Auto-Start on Boot (Recommended)

Enable systemd service:
```bash
sudo systemctl enable smart-glasses-webapp.service
sudo systemctl start smart-glasses-webapp.service
```

Check status:
```bash
sudo systemctl status smart-glasses-webapp.service
```

Now web app starts automatically when Pi boots!

---

## 📊 Dashboard Page

**URL:** `http://raspberrypi.local:5000/`

### Features:

#### System Status
- **Running/Stopped Indicator**
  - Green pulsing dot = Inference running
  - Red dot = Stopped
  
#### Current Sign Display
- Large text showing detected sign
- Updates in real-time via WebSocket
- Shows "---" when no sign detected

#### Confidence & FPS
- Confidence percentage (0-100%)
- Current FPS (frames per second)
- Updates live during inference

#### Control Buttons
- **▶️ Start Button** — Starts ISL recognition engine
- **⏹️ Stop Button** — Stops recognition engine
- Instant feedback on success/failure

#### Quick Links
- Bluetooth, Settings, Collect, Train buttons
- One-tap access to all features

### How to Use:

1. **Check Status** — Verify system is ready
2. **Start Inference** — Tap "▶️ Start" button
3. **Show Signs** — Perform ISL signs in front of glasses camera
4. **Watch Detection** — See recognized signs appear in real-time
5. **Stop When Done** — Tap "⏹️ Stop" button

**Pro Tip:** Keep dashboard open while using glasses to monitor FPS and confidence.

---

## 🔵 Bluetooth Page

**URL:** `http://raspberrypi.local:5000/bluetooth`

### No More Command Line! 🎉

Pair and connect Bluetooth speakers entirely from your phone.

### Features:

#### Scan for Devices
- **🔍 Scan Button** — Discovers nearby Bluetooth devices
- Shows spinner during scan (10 seconds)
- Lists all found devices with names and MAC addresses

#### Device List
Each device shows:
- **Device Name** (e.g., "JBL Speaker")
- **MAC Address** (e.g., "00:11:22:33:44:55")
- **Four Action Buttons:**

#### Action Buttons

**1. Pair Button (Blue)**
- Pairs Pi with the device
- Must be done before connecting
- Only needed once per device

**2. Trust Button (Blue)**
- Marks device as trusted
- Auto-connects on boot (optional)
- Recommended for your main speaker

**3. Connect Button (Green)**
- Establishes audio connection
- Must pair first
- Takes 5-10 seconds

**4. Disconnect Button (Red)**
- Closes connection
- Device remains paired
- Use when switching speakers

### Step-by-Step Pairing:

1. **Put Speaker in Pairing Mode**
   - Usually: Hold power button until blinking
   - Check speaker manual for specific instructions

2. **Open Bluetooth Page**
   - Navigate to Bluetooth tab
   - Tap "🔍 Scan for Devices"

3. **Wait for Scan**
   - Takes ~10 seconds
   - Your speaker should appear in list

4. **Pair Device**
   - Find your speaker in list
   - Tap "Pair" button
   - Wait for success message

5. **Trust Device (Optional)**
   - Tap "Trust" button
   - Allows auto-reconnect

6. **Connect**
   - Tap "Connect" button
   - Wait 5-10 seconds
   - Success message appears

7. **Test Audio**
   - Go to Dashboard
   - Start inference
   - Perform a sign
   - Listen for TTS through speaker

### Troubleshooting:

**Device Not Found:**
- Ensure speaker is in pairing mode
- Move speaker closer to Pi
- Scan again

**Pairing Failed:**
- Speaker may already be paired to another device
- Unpair from other devices first
- Restart speaker and try again

**Connection Drops:**
- Check battery level on speaker
- Reduce distance to <5 meters
- Minimize obstacles between Pi and speaker

**No Audio Output:**
- Check speaker volume
- Verify speaker is selected as audio output
- Restart PulseAudio: See troubleshooting section

---

## ⚙️ Settings Page

**URL:** `http://raspberrypi.local:5000/settings`

### Configuration Options:

#### 1. Confidence Threshold (0.5 - 0.99)
**Default:** 0.7 (70%)

- **Lower (0.5-0.6):** More detections, more false positives
- **Medium (0.7-0.8):** Balanced (recommended)
- **Higher (0.85-0.99):** Only very confident predictions

**When to Adjust:**
- **Increase** if getting false detections
- **Decrease** if missing real signs

#### 2. Stability Frames (5 - 30)
**Default:** 15

Number of consecutive identical predictions required before announcing.

- **Lower (5-10):** Faster response, less stable
- **Medium (15-20):** Balanced (recommended)
- **Higher (25-30):** Very stable, slower response

**When to Adjust:**
- **Increase** if announcing too quickly/incorrectly
- **Decrease** if response feels sluggish

#### 3. Cooldown Seconds (1 - 10)
**Default:** 3

Minimum time between repeated announcements of the same sign.

- **Lower (1-2):** Allows rapid repeated signs
- **Medium (3-4):** Comfortable (recommended)
- **Higher (5-10):** Prevents all repetition

**When to Adjust:**
- **Increase** if sign repeats annoyingly
- **Decrease** if need to repeat signs quickly

#### 4. Speech Rate (100 - 300 WPM)
**Default:** 150

Words per minute for text-to-speech.

- **Slower (100-130):** Clearer, easier to understand
- **Medium (140-170):** Natural speech pace (recommended)
- **Faster (180-300):** Rapid, harder to understand

**When to Adjust:**
- **Increase** for experienced users
- **Decrease** for first-time listeners or noisy environments

#### 5. Speech Volume (0.1 - 1.0)
**Default:** 0.9

TTS volume level (0.1 = 10%, 1.0 = 100%)

- Adjust based on speaker volume
- Higher volume may cause distortion
- Lower volume saves battery slightly

#### 6. Camera Source
**Default:** 0

- **Camera 0** — Default USB or CSI camera
- **Camera 1** — Secondary camera (if available)
- **Pi Camera** — Use Picamera2 interface (Raspberry Pi only)

**When to Change:**
- If wrong camera is being used
- To test different camera modules

### Buttons:

**💾 Save Settings**
- Saves all changes to `config.json`
- Takes effect immediately
- Persists across reboots

**🔄 Reset to Defaults**
- Restores all settings to original values
- Requires confirmation
- Page reloads automatically

### Best Settings for Different Scenarios:

**Scenario 1: Demo/Presentation**
```
Confidence: 0.8 (high)
Stability: 20 (very stable)
Cooldown: 5 (prevent repeats)
Speech Rate: 140 (clear)
```

**Scenario 2: Daily Use**
```
Confidence: 0.7 (balanced)
Stability: 15 (responsive)
Cooldown: 3 (comfortable)
Speech Rate: 160 (natural)
```

**Scenario 3: Testing/Development**
```
Confidence: 0.6 (sensitive)
Stability: 10 (fast)
Cooldown: 2 (rapid)
Speech Rate: 180 (quick feedback)
```

---

## 📊 Data Collection Page

**URL:** `http://raspberrypi.local:5000/collect`

### Remote Data Collection

Collect training data without SSH!

### Features:

#### Collection Form

**Sign Name Input**
- Enter name of sign to collect
- Examples: "Hello", "Thanks", "A", "Goodbye"
- Case-sensitive (use consistent naming)

**Number of Samples**
- Default: 200
- Range: 50-1000
- More samples = better accuracy

**▶️ Start Collection Button**
- Begins data collection on Pi
- Camera on glasses starts capturing
- Perform sign repeatedly in front of camera

#### Collection Status
- Shows when collection is active
- Displays sample count (updates live via WebSocket)
- Instructions remind you to show sign to Pi camera

#### Collected Signs List
- Shows all previously collected signs
- Displays sample count for each
- **🔄 Refresh** button updates list

### How to Use:

1. **Enter Sign Name** (e.g., "Hello")
2. **Set Sample Count** (default 200 is good)
3. **Tap Start Collection**
4. **Put on Glasses** (or position Pi camera toward you)
5. **Perform Sign Repeatedly**
   - Show sign clearly
   - Vary angles, distances, positions
   - Take short breaks to change position
6. **Wait for Completion**
   - Collection stops automatically after target samples
   - Check "Collected Signs" list to verify

**Pro Tip:** Use this page to collect data from multiple people without giving them Pi access!

---

## 🧠 Training Page

**URL:** `http://raspberrypi.local:5000/train`

### Remote Model Training

Train your ISL model from your phone!

### Features:

#### Start Training Button
- **▶️ Start Training** — Begins model training on Pi
- Button disables during training
- Training runs in background (can close page)

#### Training Status
- Shows training is in progress
- Real-time log output via WebSocket
- See epochs, loss, accuracy as they happen

#### Training Log Viewer
- Scrollable text area
- Auto-scrolls to latest output
- Shows full training details:
  ```
  Loading data...
  Found 5 sign classes
  Training samples: 800
  Epoch 1/100: loss: 1.45, accuracy: 0.42
  Epoch 2/100: loss: 0.89, accuracy: 0.68
  ...
  Training complete!
  Final accuracy: 94%
  ```

#### Training Complete
- Success message when done
- Shows final accuracy
- **📊 View Training Plot** button opens saved plot image

### How to Use:

1. **Ensure Data is Collected** (check Collection page)
2. **Tap Start Training**
3. **Wait** (5-30 minutes depending on data size)
4. **Monitor Progress** in log viewer
5. **View Results** when complete

**Training Time Estimates:**
- 500 samples: ~3 minutes
- 1000 samples: ~5 minutes
- 5000 samples: ~15 minutes
- 10000 samples: ~30 minutes

**What if training fails?**
- Check logs for error messages
- Ensure at least 3 sign classes collected
- Verify each class has 50+ samples
- Check Pi has enough RAM (close other programs)

---

## 📋 Logs Page

**URL:** `http://raspberrypi.local:5000/logs`

### Live System Monitoring

View real-time logs from Smart Glasses system.

### Features:

#### Log Viewer
- Scrollable text area
- Monospace font for readability
- Auto-scrolls to latest entries
- Shows all logged events:
  ```
  2026-02-16 13:45:23 - INFO - Smart Glasses Starting
  2026-02-16 13:45:24 - INFO - Loading TFLite model
  2026-02-16 13:45:25 - INFO - Model loaded with 5 classes
  2026-02-16 13:45:26 - INFO - Camera ready
  2026-02-16 13:45:27 - INFO - Smart Glasses running!
  2026-02-16 13:45:45 - INFO - Detected: Hello (0.92)
  2026-02-16 13:45:58 - INFO - Detected: Thanks (0.88)
  ```

#### Control Buttons

**🔄 Refresh Logs**
- Manually reloads logs from file
- Use if auto-refresh seems stuck

**🗑️ Clear Display**
- Clears log viewer (display only)
- Doesn't delete actual log file
- Click Refresh to reload

#### Auto-Refresh
- Logs auto-refresh every 5 seconds
- Always shows latest entries
- Disable by closing page

### What to Look For:

**Normal Operation:**
```
INFO - FPS: 15.2
INFO - Detected: Hello (0.89)
INFO - Detected: Thanks (0.91)
```

**Warnings (Usually OK):**
```
WARNING - Low confidence: 0.65
WARNING - No hands detected
```

**Errors (Need Attention):**
```
ERROR - Camera connection lost
ERROR - Model file not found
ERROR - Bluetooth connection failed
```

### Troubleshooting with Logs:

**Problem: No detections**
```
Look for:
"No hands detected" (repeated) → Check camera position
"Low confidence" → Lower threshold in Settings
"FPS: 5" → Pi overloaded, reduce resolution
```

**Problem: False detections**
```
Look for:
"Detected: X (0.60)" → Increase threshold
"Buffer filled too quickly" → Increase stability frames
```

**Problem: Slow response**
```
Look for:
"FPS: 8" → Pi overloaded
"Inference time: 120ms" → Model too complex
```

---

## 🔌 Web App Architecture (Advanced)

### Technology Stack:
- **Flask 3.0** — Web framework
- **Flask-SocketIO** — Real-time WebSocket communication
- **Eventlet** — Async server for SocketIO
- **HTML/CSS/JavaScript** — Frontend
- **No external CDNs** — Works offline

### Real-Time Updates:

The webapp uses WebSockets for live updates:

```javascript
// Dashboard receives inference updates
socket.on('inference_update', function(data) {
    display.text = data.current_sign;
    display.confidence = data.confidence;
    display.fps = data.fps;
});

// Training page receives training progress
socket.on('training_progress', function(data) {
    logViewer.append(data.message);
});
```

### API Endpoints:

**Status:**
- `GET /api/status` — Get system status

**Inference Control:**
- `POST /api/start_inference` — Start recognition
- `POST /api/stop_inference` — Stop recognition

**Bluetooth:**
- `POST /api/bluetooth/scan` — Scan for devices
- `POST /api/bluetooth/pair` — Pair device
- `POST /api/bluetooth/trust` — Trust device
- `POST /api/bluetooth/connect` — Connect device
- `POST /api/bluetooth/disconnect` — Disconnect device

**Settings:**
- `POST /api/settings/save` — Save configuration
- `POST /api/settings/reset` — Reset to defaults

**Data Collection:**
- `POST /api/collect/start` — Start collection
- `GET /api/collect/list` — List collected signs

**Training:**
- `POST /api/train/start` — Start training

**Logs:**
- `GET /api/logs/get` — Get log contents

---

## 🚨 Troubleshooting

### Web App Won't Load

**Problem:** Page not loading or "Connection refused"

**Solutions:**
1. Check Pi is powered on and connected to WiFi
2. Verify web app service is running:
   ```bash
   sudo systemctl status smart-glasses-webapp.service
   ```
3. Check firewall:
   ```bash
   sudo ufw allow 5000
   ```
4. Try IP address instead of hostname
5. Restart web app:
   ```bash
   sudo systemctl restart smart-glasses-webapp.service
   ```

### Page Loads But Features Don't Work

**Problem:** Buttons don't respond or updates don't show

**Solutions:**
1. Check JavaScript errors in browser console (F12)
2. Verify WebSocket connection (should see "Connected" in console)
3. Clear browser cache
4. Try different browser
5. Check Pi logs for errors:
   ```bash
   sudo journalctl -u smart-glasses-webapp -f
   ```

### Bluetooth Controls Not Working

**Problem:** Scan/pair/connect buttons fail

**Solutions:**
1. Ensure bluetoothctl is installed:
   ```bash
   which bluetoothctl
   ```
2. Check Bluetooth service:
   ```bash
   sudo systemctl status bluetooth
   ```
3. Verify Pi has Bluetooth (not all models do)
4. Try manual pairing first via SSH to debug

### Settings Not Saving

**Problem:** Changes reset after refresh

**Solutions:**
1. Check file permissions:
   ```bash
   ls -la config.json
   chmod 664 config.json
   ```
2. Check disk space:
   ```bash
   df -h
   ```
3. Verify config.json is not corrupted
4. Try manual edit and restart

---

## 💡 Pro Tips

### 1. Bookmark the Dashboard
Add to your phone's home screen for quick access:
- **iOS:** Safari → Share → Add to Home Screen
- **Android:** Chrome → Menu → Add to Home Screen

### 2. Use Multiple Devices
Multiple phones can connect simultaneously:
- One person controls (Dashboard)
- Another monitors (Logs)
- Another trains models (Training)

### 3. Battery Monitoring
Add USB power meter to monitor Pi power consumption in real-time.

### 4. Dark Theme
Web app uses dark theme by default (easy on eyes, saves battery).

### 5. Offline Mode
Web app works without internet — only needs local WiFi to Pi.

---

## 🔐 Security Considerations

### Current Security:
- ⚠️ No authentication (anyone on same WiFi can access)
- ⚠️ No HTTPS (traffic not encrypted)
- ✅ Local network only (not exposed to internet)

### For Production Use:

**Add Authentication:**
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify(username, password):
    return username == 'admin' and password == 'your-password'

@app.route('/bluetooth')
@auth.login_required
def bluetooth():
    ...
```

**Enable HTTPS:**
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

# Run with SSL
socketio.run(app, host='0.0.0.0', port=5000, 
             certfile='cert.pem', keyfile='key.pem')
```

**Firewall Rules:**
```bash
# Only allow specific IPs
sudo ufw allow from 192.168.1.100 to any port 5000
```

---

## 📚 Additional Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **Flask-SocketIO**: https://flask-socketio.readthedocs.io/
- **Mobile Web App Best Practices**: https://web.dev/mobile/

---

**Questions?** Open an issue on GitHub!

**Need help?** Check logs first, then create a GitHub issue with log output.

---

**Enjoy controlling your Smart Glasses from your phone! 📱🤟**
