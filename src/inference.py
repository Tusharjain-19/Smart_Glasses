"""
Real-time ISL Inference with Text-to-Speech
Recognizes ISL signs from webcam and converts to speech.
"""

import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import threading
import time
import argparse
import json
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils import extract_landmarks, load_model_and_labels, draw_landmarks_on_frame


class TTSEngine:
    """Thread-safe Text-to-Speech engine."""
    
    def __init__(self, rate=150, volume=0.9):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)
        self.engine.setProperty('volume', volume)
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
                print(f"TTS Error: {e}")
            finally:
                self.is_speaking = False


def main():
    parser = argparse.ArgumentParser(description='Real-time ISL recognition with TTS')
    parser.add_argument('--config', type=str, default='config.json', help='Configuration file')
    parser.add_argument('--camera', type=int, default=0, help='Camera index')
    args = parser.parse_args()
    
    # Load configuration
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    else:
        print(f"Warning: Config file {args.config} not found, using defaults")
        config = {
            'confidence_threshold': 0.7,
            'stability_frames': 15,
            'cooldown_seconds': 3,
            'speech_rate': 150,
            'speech_volume': 0.9,
            'camera_width': 640,
            'camera_height': 480,
            'model_path': 'models/isl_model.keras',
            'labels_path': 'models/labels.npy'
        }
    
    print("=== ISL Real-time Recognition ===\n")
    print("Loading model...")
    
    # Load model and labels
    try:
        model, labels = load_model_and_labels(
            config['model_path'],
            config['labels_path']
        )
        print(f"✓ Model loaded")
        print(f"✓ Classes: {list(labels)}\n")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please train a model first using train_model.py")
        return
    
    # Initialize TTS
    print("Initializing Text-to-Speech...")
    tts = TTSEngine(
        rate=config.get('speech_rate', 150),
        volume=config.get('speech_volume', 0.9)
    )
    print("✓ TTS ready\n")
    
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    
    # Open webcam
    cap = cv2.VideoCapture(args.camera)
    
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.get('camera_width', 640))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.get('camera_height', 480))
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Recognition variables
    stability_buffer = []
    last_announced_sign = None
    last_announcement_time = 0
    
    confidence_threshold = config.get('confidence_threshold', 0.7)
    stability_frames = config.get('stability_frames', 15)
    cooldown_seconds = config.get('cooldown_seconds', 3)
    
    print("Instructions:")
    print("  - Show ISL signs to the camera")
    print("  - Press 'R' to reset buffer")
    print("  - Press 'Q' to quit")
    print("\nStarting inference...\n")
    
    fps_counter = 0
    fps_start_time = time.time()
    current_fps = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                break
            
            # Flip frame horizontally
            frame = cv2.flip(frame, 1)
            
            # Extract landmarks
            landmarks = extract_landmarks(frame, hands)
            
            predicted_sign = None
            confidence = 0.0
            
            if landmarks is not None:
                # Draw landmarks
                frame = draw_landmarks_on_frame(frame, hands)
                
                # Predict
                landmarks_input = landmarks.reshape(1, -1)
                prediction = model.predict(landmarks_input, verbose=0)[0]
                
                max_idx = np.argmax(prediction)
                confidence = prediction[max_idx]
                
                if confidence >= confidence_threshold:
                    predicted_sign = labels[max_idx]
                    
                    # Add to stability buffer
                    stability_buffer.append(predicted_sign)
                    
                    # Keep buffer at stability_frames length
                    if len(stability_buffer) > stability_frames:
                        stability_buffer.pop(0)
                    
                    # Check if buffer is stable (all same sign)
                    if len(stability_buffer) == stability_frames and \
                       all(s == predicted_sign for s in stability_buffer):
                        
                        current_time = time.time()
                        
                        # Check cooldown
                        if predicted_sign != last_announced_sign or \
                           (current_time - last_announcement_time) > cooldown_seconds:
                            
                            # Announce the sign
                            print(f"Detected: {predicted_sign} ({confidence:.2%})")
                            tts.speak(predicted_sign)
                            
                            last_announced_sign = predicted_sign
                            last_announcement_time = current_time
                            
                            # Clear buffer after announcement
                            stability_buffer.clear()
                else:
                    # Low confidence, clear buffer
                    stability_buffer.clear()
            else:
                # No hands detected, clear buffer
                stability_buffer.clear()
            
            # Calculate FPS
            fps_counter += 1
            if time.time() - fps_start_time >= 1.0:
                current_fps = fps_counter
                fps_counter = 0
                fps_start_time = time.time()
            
            # Display information
            display_height = frame.shape[0]
            display_width = frame.shape[1]
            
            # Dark overlay for text
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (display_width, 150), (0, 0, 0), -1)
            frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
            
            # Display predicted sign
            if predicted_sign and confidence >= confidence_threshold:
                cv2.putText(frame, f"Sign: {predicted_sign}", (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
                cv2.putText(frame, f"Confidence: {confidence:.1%}", (10, 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Sign: ---", (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (128, 128, 128), 2)
            
            # Display stability bar
            stability_progress = len(stability_buffer) / stability_frames
            bar_width = int(300 * stability_progress)
            cv2.rectangle(frame, (10, 100), (310, 120), (50, 50, 50), -1)
            if bar_width > 0:
                cv2.rectangle(frame, (10, 100), (10 + bar_width, 120), (0, 255, 255), -1)
            cv2.putText(frame, f"Stability: {len(stability_buffer)}/{stability_frames}",
                       (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Display cooldown indicator
            current_time = time.time()
            time_since_last = current_time - last_announcement_time
            if time_since_last < cooldown_seconds:
                cooldown_remaining = cooldown_seconds - time_since_last
                cv2.putText(frame, f"Cooldown: {cooldown_remaining:.1f}s",
                           (display_width - 200, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            
            # Display FPS
            cv2.putText(frame, f"FPS: {current_fps}", (display_width - 150, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Instructions
            cv2.putText(frame, "Press 'R' to reset, 'Q' to quit",
                       (10, display_height - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # Show frame
            cv2.imshow('ISL Recognition', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == ord('Q'):
                print("\nQuitting...")
                break
            elif key == ord('r') or key == ord('R'):
                stability_buffer.clear()
                last_announced_sign = None
                print("Buffer reset")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        hands.close()
        print("Cleanup complete")


if __name__ == "__main__":
    main()
