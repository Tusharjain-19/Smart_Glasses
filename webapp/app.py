"""
Flask Web App for Smart Glasses Mobile Control Panel
Provides mobile interface for Bluetooth pairing, settings, data collection, and training.
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import subprocess
import json
import os
import time
import threading
import sys
import signal

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-glasses-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Global state
inference_process = None
collection_process = None
training_process = None
app_state = {
    'inference_running': False,
    'current_sign': None,
    'confidence': 0.0,
    'fps': 0,
    'battery_level': 100  # Placeholder
}


def load_config():
    """Load configuration from config.json."""
    config_path = 'config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def save_config(config):
    """Save configuration to config.json."""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)


def run_command(command, timeout=10):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


# ============= Routes =============

@app.route('/')
def index():
    """Dashboard page."""
    return render_template('index.html')


@app.route('/bluetooth')
def bluetooth():
    """Bluetooth management page."""
    return render_template('bluetooth.html')


@app.route('/settings')
def settings():
    """Settings page."""
    config = load_config()
    return render_template('settings.html', config=config)


@app.route('/collect')
def collect():
    """Data collection page."""
    return render_template('collect.html')


@app.route('/train')
def train():
    """Training page."""
    return render_template('train.html')


@app.route('/logs')
def logs():
    """Logs page."""
    return render_template('logs.html')


# ============= API Endpoints =============

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status."""
    return jsonify(app_state)


@app.route('/api/start_inference', methods=['POST'])
def start_inference():
    """Start inference engine."""
    global inference_process, app_state
    
    if inference_process and inference_process.poll() is None:
        return jsonify({'success': False, 'message': 'Inference already running'})
    
    try:
        # Start deploy_pi.py or inference.py
        script_path = 'src/deploy_pi.py'
        if not os.path.exists(script_path):
            script_path = 'src/inference.py'
        
        inference_process = subprocess.Popen(
            ['python3', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        app_state['inference_running'] = True
        
        # Monitor process in background
        threading.Thread(target=monitor_inference, daemon=True).start()
        
        return jsonify({'success': True, 'message': 'Inference started'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/stop_inference', methods=['POST'])
def stop_inference():
    """Stop inference engine."""
    global inference_process, app_state
    
    if not inference_process or inference_process.poll() is not None:
        return jsonify({'success': False, 'message': 'Inference not running'})
    
    try:
        inference_process.send_signal(signal.SIGINT)
        inference_process.wait(timeout=5)
        app_state['inference_running'] = False
        app_state['current_sign'] = None
        
        return jsonify({'success': True, 'message': 'Inference stopped'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


def monitor_inference():
    """Monitor inference process and emit updates via SocketIO."""
    global inference_process, app_state
    
    while inference_process and inference_process.poll() is None:
        # In a real implementation, you would parse logs or use IPC
        # For now, just emit status updates
        socketio.emit('inference_update', app_state)
        time.sleep(1)
    
    app_state['inference_running'] = False
    socketio.emit('inference_update', app_state)


@app.route('/api/bluetooth/scan', methods=['POST'])
def bluetooth_scan():
    """Scan for Bluetooth devices."""
    try:
        # Use bluetoothctl to scan
        success, stdout, stderr = run_command('bluetoothctl devices', timeout=10)
        
        if success:
            devices = []
            for line in stdout.strip().split('\n'):
                if line.startswith('Device'):
                    parts = line.split(maxsplit=2)
                    if len(parts) >= 3:
                        devices.append({
                            'mac': parts[1],
                            'name': parts[2]
                        })
            
            return jsonify({'success': True, 'devices': devices})
        else:
            return jsonify({'success': False, 'message': stderr})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/bluetooth/pair', methods=['POST'])
def bluetooth_pair():
    """Pair with a Bluetooth device."""
    data = request.json
    mac = data.get('mac')
    
    if not mac:
        return jsonify({'success': False, 'message': 'No MAC address provided'})
    
    try:
        # Pair with device
        success, stdout, stderr = run_command(f'bluetoothctl pair {mac}', timeout=30)
        
        if success or 'AlreadyExists' in stderr:
            return jsonify({'success': True, 'message': 'Device paired'})
        else:
            return jsonify({'success': False, 'message': stderr})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/bluetooth/trust', methods=['POST'])
def bluetooth_trust():
    """Trust a Bluetooth device."""
    data = request.json
    mac = data.get('mac')
    
    if not mac:
        return jsonify({'success': False, 'message': 'No MAC address provided'})
    
    try:
        success, stdout, stderr = run_command(f'bluetoothctl trust {mac}', timeout=10)
        
        if success:
            return jsonify({'success': True, 'message': 'Device trusted'})
        else:
            return jsonify({'success': False, 'message': stderr})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/bluetooth/connect', methods=['POST'])
def bluetooth_connect():
    """Connect to a Bluetooth device."""
    data = request.json
    mac = data.get('mac')
    
    if not mac:
        return jsonify({'success': False, 'message': 'No MAC address provided'})
    
    try:
        success, stdout, stderr = run_command(f'bluetoothctl connect {mac}', timeout=20)
        
        if success or 'Connected: yes' in stdout:
            return jsonify({'success': True, 'message': 'Device connected'})
        else:
            return jsonify({'success': False, 'message': stderr})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/bluetooth/disconnect', methods=['POST'])
def bluetooth_disconnect():
    """Disconnect from a Bluetooth device."""
    data = request.json
    mac = data.get('mac')
    
    if not mac:
        return jsonify({'success': False, 'message': 'No MAC address provided'})
    
    try:
        success, stdout, stderr = run_command(f'bluetoothctl disconnect {mac}', timeout=10)
        
        if success:
            return jsonify({'success': True, 'message': 'Device disconnected'})
        else:
            return jsonify({'success': False, 'message': stderr})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/settings/save', methods=['POST'])
def save_settings():
    """Save settings."""
    data = request.json
    
    try:
        config = load_config()
        config.update(data)
        save_config(config)
        
        return jsonify({'success': True, 'message': 'Settings saved'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/settings/reset', methods=['POST'])
def reset_settings():
    """Reset settings to defaults."""
    try:
        default_config = {
            'confidence_threshold': 0.7,
            'stability_frames': 15,
            'cooldown_seconds': 3,
            'speech_rate': 150,
            'speech_volume': 0.9,
            'camera_source': 0,
            'camera_width': 640,
            'camera_height': 480,
            'pi_camera_width': 320,
            'pi_camera_height': 240,
            'model_path': 'models/isl_model.keras',
            'tflite_model_path': 'models/isl_model.tflite',
            'labels_path': 'models/labels.npy',
            'data_dir': 'data',
            'log_file': 'logs/smart_glasses.log'
        }
        
        save_config(default_config)
        
        return jsonify({'success': True, 'message': 'Settings reset to defaults', 'config': default_config})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/collect/start', methods=['POST'])
def start_collection():
    """Start data collection."""
    global collection_process
    
    data = request.json
    sign_name = data.get('sign')
    num_samples = data.get('samples', 200)
    
    if not sign_name:
        return jsonify({'success': False, 'message': 'No sign name provided'})
    
    if collection_process and collection_process.poll() is None:
        return jsonify({'success': False, 'message': 'Collection already running'})
    
    try:
        collection_process = subprocess.Popen(
            ['python3', 'src/collect_data.py', '--sign', sign_name, '--samples', str(num_samples)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return jsonify({'success': True, 'message': f'Started collecting {sign_name}'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/collect/list', methods=['GET'])
def list_collected():
    """List collected sign data."""
    try:
        data_dir = 'data'
        if not os.path.exists(data_dir):
            return jsonify({'success': True, 'signs': []})
        
        signs = []
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                sign_name = filename.replace('.csv', '')
                filepath = os.path.join(data_dir, filename)
                
                # Count lines in CSV (subtract 1 for header)
                with open(filepath, 'r') as f:
                    num_samples = sum(1 for line in f) - 1
                
                signs.append({
                    'name': sign_name,
                    'samples': num_samples
                })
        
        return jsonify({'success': True, 'signs': signs})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/train/start', methods=['POST'])
def start_training():
    """Start model training."""
    global training_process
    
    if training_process and training_process.poll() is None:
        return jsonify({'success': False, 'message': 'Training already running'})
    
    try:
        training_process = subprocess.Popen(
            ['python3', 'src/train_model.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Monitor training in background
        threading.Thread(target=monitor_training, daemon=True).start()
        
        return jsonify({'success': True, 'message': 'Training started'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


def monitor_training():
    """Monitor training process and emit progress via SocketIO."""
    global training_process
    
    while training_process and training_process.poll() is None:
        line = training_process.stdout.readline()
        if line:
            socketio.emit('training_progress', {'message': line.strip()})
    
    # Training complete
    socketio.emit('training_complete', {'message': 'Training finished'})


@app.route('/api/logs/get', methods=['GET'])
def get_logs():
    """Get application logs."""
    try:
        log_file = 'logs/smart_glasses.log'
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.read()
            
            return jsonify({'success': True, 'logs': logs})
        else:
            return jsonify({'success': True, 'logs': 'No logs available'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# ============= SocketIO Events =============

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('connected', {'message': 'Connected to Smart Glasses'})


@socketio.on('request_status')
def handle_status_request():
    """Handle status request."""
    emit('status_update', app_state)


if __name__ == '__main__':
    print("=== Smart Glasses Web App ===")
    print("Starting server on http://0.0.0.0:5000")
    print("Access from your phone: http://<pi-ip-address>:5000")
    print("Or: http://raspberrypi.local:5000")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
