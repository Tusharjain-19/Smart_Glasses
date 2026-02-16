"""
Utility functions for Smart Glasses ISL Recognition System
"""

import numpy as np
import cv2
import mediapipe as mp
from tensorflow import keras


def extract_landmarks(frame, hands):
    """
    Extract hand landmarks from a frame using MediaPipe Hands.
    
    Args:
        frame: Input frame (BGR image)
        hands: MediaPipe Hands solution object
    
    Returns:
        numpy array of shape (126,) containing normalized landmarks for both hands
        or None if no hands detected
    """
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        landmarks = []
        
        # Process up to 2 hands
        for i in range(min(2, len(results.multi_hand_landmarks))):
            hand_landmarks = results.multi_hand_landmarks[i]
            
            # Extract x, y, z coordinates for all 21 landmarks
            for landmark in hand_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z])
        
        # Pad with zeros if only one hand detected (63 features per hand)
        while len(landmarks) < 126:
            landmarks.append(0.0)
        
        # Normalize the landmarks
        landmarks_array = np.array(landmarks[:126])
        normalized = normalize_landmarks(landmarks_array)
        
        return normalized
    
    return None


def normalize_landmarks(landmarks):
    """
    Normalize landmarks relative to wrist position.
    
    Args:
        landmarks: numpy array of shape (126,) containing raw landmark coordinates
    
    Returns:
        Normalized numpy array of shape (126,)
    """
    landmarks = landmarks.copy()
    
    # Normalize each hand separately (first 63, then next 63)
    for hand_idx in range(2):
        start_idx = hand_idx * 63
        end_idx = start_idx + 63
        
        # Check if this hand has data (non-zero)
        if np.any(landmarks[start_idx:end_idx]):
            # Get wrist coordinates (first landmark of each hand)
            wrist_x = landmarks[start_idx]
            wrist_y = landmarks[start_idx + 1]
            wrist_z = landmarks[start_idx + 2]
            
            # Normalize all landmarks relative to wrist
            for i in range(start_idx, end_idx, 3):
                landmarks[i] -= wrist_x      # x coordinate
                landmarks[i + 1] -= wrist_y  # y coordinate
                landmarks[i + 2] -= wrist_z  # z coordinate
    
    return landmarks


def load_model_and_labels(model_path, labels_path):
    """
    Load trained Keras model and label list.
    
    Args:
        model_path: Path to .keras model file
        labels_path: Path to .npy labels file
    
    Returns:
        Tuple of (model, labels)
    """
    model = keras.models.load_model(model_path)
    labels = np.load(labels_path, allow_pickle=True)
    return model, labels


def load_tflite_model(model_path):
    """
    Load TensorFlow Lite model for Raspberry Pi.
    
    Args:
        model_path: Path to .tflite model file
    
    Returns:
        TFLite Interpreter object
    """
    import tensorflow as tf
    
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter


def predict_tflite(interpreter, input_data):
    """
    Run inference using TFLite interpreter.
    
    Args:
        interpreter: TFLite Interpreter object
        input_data: Input numpy array
    
    Returns:
        Prediction probabilities array
    """
    # Get input and output tensors
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # Prepare input
    input_data = np.array(input_data, dtype=np.float32).reshape(1, -1)
    
    # Set input tensor
    interpreter.set_tensor(input_details[0]['index'], input_data)
    
    # Run inference
    interpreter.invoke()
    
    # Get output
    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data[0]


def get_sign_text(prediction, labels, threshold=0.7):
    """
    Get sign text from prediction if confidence is above threshold.
    
    Args:
        prediction: Probability array from model
        labels: List of label names
        threshold: Minimum confidence threshold
    
    Returns:
        Tuple of (sign_text, confidence) or (None, 0.0) if below threshold
    """
    max_idx = np.argmax(prediction)
    confidence = prediction[max_idx]
    
    if confidence >= threshold:
        return labels[max_idx], float(confidence)
    
    return None, float(confidence)


def draw_landmarks_on_frame(frame, hands):
    """
    Draw MediaPipe hand landmarks on frame.
    
    Args:
        frame: Input frame (BGR image)
        hands: MediaPipe Hands solution object
    
    Returns:
        Frame with landmarks drawn
    """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
    
    return frame
