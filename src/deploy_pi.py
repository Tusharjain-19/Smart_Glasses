"""
Raspberry Pi Deployment Script for Smart Glasses
Optimized for Pi Zero 2W with TFLite, Picamera2, and Bluetooth audio.
"""

import numpy as np
import cv2
import mediapipe as mp
import pyttsx3
import threading
import time
import json
import os
import sys
import logging
import subprocess

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import normalize_landmarks, load_tflite_model, predict_tflite


class TTSEngine:
    """Thread-safe Text-to-Speech engine for Raspberry Pi."""
    
    def __init__(self, rate=150, volume=0.9):
        try:
            self.engine = pyttsx3.init(driverName='espeak')
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
        except Exception as e:
            logging.warning(f"Could not initialize espeak, falling back to default: {e}")
            self.engine = pyttsx3.init()
        
        self.lock = threading.Lock()
        self.is_speaking = False
    
    def speak(self, text):
        """Speak text in a separate thread."""
        if not self.is_speaking:
            thread = threading.Thread(target=self._speak_thread, args=(text,))
            thread.daemon = True
            thread.start()
    
    def _speak_thread(self, text):
        """Internal method to speak text."""
        with self.lock:
            self.is_speaking = True
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logging.error(f"TTS Error: {e}")
            finally:
                self.is_speaking = False


class PiCamera:
    """Wrapper for Picamera2 with OpenCV fallback."""
    
    def __init__(self, width=320, height=240):
        self.width = width
        self.height = height
        self.cap = None
        self.use_picamera = False
        
        # Try Picamera2 first
        try:
            from picamera2 import Picamera2
            self.picam = Picamera2()
            config = self.picam.create_preview_configuration(
                main={"size": (width, height), "format": "RGB888"}
            )
            self.picam.configure(config)
            self.picam.start()
            self.use_picamera = True
            logging.info("Using Picamera2")
        except Exception as e:
            logging.warning(f"Picamera2 not available, using OpenCV: {e}")
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
    
    def read(self):
        """Read a frame from camera."""
        if self.use_picamera:
            frame = self.picam.capture_array()
            # Picamera2 returns RGB, convert to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return True, frame
        else:
            return self.cap.read()
    
    def release(self):
        """Release camera resources."""
        if self.use_picamera:
            self.picam.stop()
        else:
            if self.cap:
                self.cap.release()


def setup_bluetooth_audio():
    """Setup Bluetooth audio output via PulseAudio."""
    try:
        # Check if PulseAudio is running
        result = subprocess.run(['pulseaudio', '--check'], 
                              capture_output=True, timeout=5)
        if result.returncode != 0:
            logging.info("Starting PulseAudio...")
            subprocess.run(['pulseaudio', '--start'], timeout=10)
        
        logging.info("Bluetooth audio setup complete")
        return True
    except Exception as e:
        logging.warning(f"Could not setup Bluetooth audio: {e}")
        return False


def extract_landmarks_pi(frame, hands):
    """Extract hand landmarks optimized for Pi."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        landmarks = []
        
        for i in range(min(2, len(results.multi_hand_landmarks))):
            hand_landmarks = results.multi_hand_landmarks[i]
            for landmark in hand_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z])
        
        while len(landmarks) < 126:
            landmarks.append(0.0)
        
        landmarks_array = np.array(landmarks[:126], dtype=np.float32)
        normalized = normalize_landmarks(landmarks_array)
        
        return normalized
    
    return None


def main():
    # Setup logging
    log_file = 'logs/smart_glasses.log'
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info("=== Smart Glasses Starting ===")
    
    # Load configuration
    config_path = 'config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        logging.warning(f"Config file {config_path} not found, using defaults")
        config = {
            'confidence_threshold': 0.7,
            'stability_frames': 15,
            'cooldown_seconds': 3,
            'speech_rate': 150,
            'speech_volume': 0.9,
            'pi_camera_width': 320,
            'pi_camera_height': 240,
            'tflite_model_path': 'models/isl_model.tflite',
            'labels_path': 'models/labels.npy'
        }
    
    # Setup Bluetooth audio
    logging.info("Setting up Bluetooth audio...")
    setup_bluetooth_audio()
    
    # Load TFLite model
    logging.info("Loading TFLite model...")
    try:
        interpreter = load_tflite_model(config['tflite_model_path'])
        labels = np.load(config['labels_path'], allow_pickle=True)
        logging.info(f"Model loaded with {len(labels)} classes")
        logging.info(f"Classes: {list(labels)}")
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        logging.error("Please train a model and convert to TFLite first")
        return
    
    # Initialize TTS
    logging.info("Initializing Text-to-Speech...")
    tts = TTSEngine(
        rate=config.get('speech_rate', 150),
        volume=config.get('speech_volume', 0.9)
    )
    logging.info("TTS ready")
    
    # Initialize MediaPipe Hands (lighter settings for Pi)
    logging.info("Initializing MediaPipe Hands...")
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,  # Lower for Pi
        min_tracking_confidence=0.5,
        model_complexity=0  # Use lite model
    )
    logging.info("MediaPipe ready")
    
    # Initialize camera
    logging.info("Initializing camera...")
    camera = PiCamera(
        width=config.get('pi_camera_width', 320),
        height=config.get('pi_camera_height', 240)
    )
    logging.info("Camera ready")
    
    # Recognition variables
    stability_buffer = []
    last_announced_sign = None
    last_announcement_time = 0
    
    confidence_threshold = config.get('confidence_threshold', 0.7)
    stability_frames = config.get('stability_frames', 15)
    cooldown_seconds = config.get('cooldown_seconds', 3)
    
    logging.info("Smart Glasses running!")
    logging.info("Press Ctrl+C to stop")
    
    frame_count = 0
    fps_start = time.time()
    
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                logging.error("Failed to capture frame")
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Extract landmarks
            landmarks = extract_landmarks_pi(frame, hands)
            
            if landmarks is not None:
                # Predict using TFLite
                prediction = predict_tflite(interpreter, landmarks)
                
                max_idx = np.argmax(prediction)
                confidence = float(prediction[max_idx])
                
                if confidence >= confidence_threshold:
                    predicted_sign = labels[max_idx]
                    
                    # Add to stability buffer
                    stability_buffer.append(predicted_sign)
                    
                    if len(stability_buffer) > stability_frames:
                        stability_buffer.pop(0)
                    
                    # Check if buffer is stable
                    if len(stability_buffer) == stability_frames and \
                       all(s == predicted_sign for s in stability_buffer):
                        
                        current_time = time.time()
                        
                        # Check cooldown
                        if predicted_sign != last_announced_sign or \
                           (current_time - last_announcement_time) > cooldown_seconds:
                            
                            logging.info(f"Detected: {predicted_sign} ({confidence:.2%})")
                            tts.speak(predicted_sign)
                            
                            last_announced_sign = predicted_sign
                            last_announcement_time = current_time
                            stability_buffer.clear()
                else:
                    stability_buffer.clear()
            else:
                stability_buffer.clear()
            
            # Log FPS every 30 frames
            if frame_count % 30 == 0:
                elapsed = time.time() - fps_start
                fps = 30 / elapsed
                logging.info(f"FPS: {fps:.1f}")
                fps_start = time.time()
            
            # Small delay to prevent CPU overload
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
    
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        import traceback
        logging.error(traceback.format_exc())
    
    finally:
        logging.info("Shutting down...")
        camera.release()
        hands.close()
        logging.info("Cleanup complete")


if __name__ == "__main__":
    main()
