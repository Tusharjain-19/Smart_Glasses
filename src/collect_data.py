"""
Data Collection Script for ISL Recognition
Collects hand landmark data for training the ISL classifier.
"""

import cv2
import mediapipe as mp
import numpy as np
import os
import argparse
import csv
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description='Collect ISL sign data')
    parser.add_argument('--sign', type=str, required=True, help='Name of the sign to collect (e.g., "A", "Hello")')
    parser.add_argument('--samples', type=int, default=200, help='Number of samples to collect (default: 200)')
    parser.add_argument('--data_dir', type=str, default='data', help='Directory to save data (default: data)')
    args = parser.parse_args()
    
    # Create data directory if it doesn't exist
    os.makedirs(args.data_dir, exist_ok=True)
    
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Data collection variables
    collecting = False
    collected_samples = 0
    data_samples = []
    
    print(f"=== ISL Data Collection ===")
    print(f"Sign: {args.sign}")
    print(f"Target samples: {args.samples}")
    print(f"Instructions:")
    print("  - Press 'S' to start/stop collecting")
    print("  - Press 'Q' to quit")
    print("  - Show the sign clearly to the camera")
    print("  - Try different angles and distances")
    print("\nWaiting for 'S' to start...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe
        results = hands.process(frame_rgb)
        
        # Draw landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                )
            
            # Collect data if collecting is active
            if collecting and collected_samples < args.samples:
                landmarks = []
                
                # Extract landmarks from up to 2 hands
                for i in range(min(2, len(results.multi_hand_landmarks))):
                    hand_landmarks = results.multi_hand_landmarks[i]
                    for landmark in hand_landmarks.landmark:
                        landmarks.extend([landmark.x, landmark.y, landmark.z])
                
                # Pad with zeros if only one hand detected
                while len(landmarks) < 126:
                    landmarks.append(0.0)
                
                # Store only first 126 features
                data_samples.append(landmarks[:126])
                collected_samples += 1
                
                # Show progress
                if collected_samples % 10 == 0:
                    print(f"Collected: {collected_samples}/{args.samples}")
        
        # Display information on frame
        status_color = (0, 255, 0) if collecting else (0, 0, 255)
        status_text = "COLLECTING" if collecting else "PAUSED"
        
        cv2.putText(frame, f"Sign: {args.sign}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Status: {status_text}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        cv2.putText(frame, f"Samples: {collected_samples}/{args.samples}", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Draw progress bar
        progress = min(collected_samples / args.samples, 1.0)
        bar_width = int(600 * progress)
        cv2.rectangle(frame, (10, 130), (610, 160), (50, 50, 50), -1)
        cv2.rectangle(frame, (10, 130), (10 + bar_width, 160), (0, 255, 0), -1)
        cv2.putText(frame, f"{int(progress * 100)}%", (620, 155),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Instructions
        cv2.putText(frame, "Press 'S' to start/stop, 'Q' to quit", (10, 460),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # Show frame
        cv2.imshow('ISL Data Collection', frame)
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') or key == ord('S'):
            collecting = not collecting
            status = "Started" if collecting else "Paused"
            print(f"\nCollection {status}")
        
        elif key == ord('q') or key == ord('Q'):
            print("\nQuitting...")
            break
        
        # Stop if we've collected enough samples
        if collected_samples >= args.samples:
            print(f"\nTarget reached! Collected {collected_samples} samples")
            collecting = False
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    
    # Save data to CSV
    if len(data_samples) > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(args.data_dir, f"{args.sign}.csv")
        
        print(f"\nSaving {len(data_samples)} samples to {filename}...")
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            header = []
            for hand_idx in range(2):
                for landmark_idx in range(21):
                    header.extend([
                        f'h{hand_idx}_l{landmark_idx}_x',
                        f'h{hand_idx}_l{landmark_idx}_y',
                        f'h{hand_idx}_l{landmark_idx}_z'
                    ])
            writer.writerow(header)
            
            # Write data
            writer.writerows(data_samples)
        
        print(f"✓ Data saved successfully!")
        print(f"  File: {filename}")
        print(f"  Samples: {len(data_samples)}")
        print(f"  Features per sample: 126")
    else:
        print("\nNo data collected. Exiting.")


if __name__ == "__main__":
    main()
