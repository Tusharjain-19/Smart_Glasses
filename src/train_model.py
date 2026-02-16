"""
Model Training Script for ISL Recognition
Trains a neural network classifier on collected landmark data.
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt
import argparse


def load_data(data_dir):
    """Load all CSV files from data directory."""
    print("Loading data...")
    
    X = []
    y = []
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if len(csv_files) == 0:
        raise ValueError(f"No CSV files found in {data_dir}")
    
    print(f"Found {len(csv_files)} sign classes:")
    
    for csv_file in csv_files:
        # Extract label from filename (without .csv extension)
        label = csv_file.replace('.csv', '')
        
        # Load CSV
        filepath = os.path.join(data_dir, csv_file)
        df = pd.read_csv(filepath)
        
        # Extract features (skip header)
        features = df.values
        
        print(f"  - {label}: {len(features)} samples")
        
        # Add to dataset
        X.extend(features)
        y.extend([label] * len(features))
    
    return np.array(X), np.array(y)


def create_model(input_shape, num_classes):
    """Create neural network model."""
    model = keras.Sequential([
        layers.Input(shape=(input_shape,)),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        layers.Dense(128, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.2),
        
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model


def plot_training_history(history, save_path):
    """Plot and save training curves."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # Plot accuracy
    ax1.plot(history.history['accuracy'], label='Train Accuracy')
    ax1.plot(history.history['val_accuracy'], label='Val Accuracy')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Accuracy')
    ax1.set_title('Model Accuracy')
    ax1.legend()
    ax1.grid(True)
    
    # Plot loss
    ax2.plot(history.history['loss'], label='Train Loss')
    ax2.plot(history.history['val_loss'], label='Val Loss')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Loss')
    ax2.set_title('Model Loss')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✓ Training plot saved to {save_path}")


def main():
    parser = argparse.ArgumentParser(description='Train ISL recognition model')
    parser.add_argument('--data_dir', type=str, default='data', help='Directory containing CSV files')
    parser.add_argument('--model_dir', type=str, default='models', help='Directory to save model')
    parser.add_argument('--epochs', type=int, default=100, help='Maximum number of epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    args = parser.parse_args()
    
    # Create models directory
    os.makedirs(args.model_dir, exist_ok=True)
    
    print("=== ISL Model Training ===\n")
    
    # Load data
    X, y = load_data(args.data_dir)
    print(f"\nTotal samples: {len(X)}")
    print(f"Features per sample: {X.shape[1]}")
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    num_classes = len(label_encoder.classes_)
    
    print(f"\nClasses ({num_classes}):", list(label_encoder.classes_))
    
    # Convert to one-hot encoding
    y_categorical = to_categorical(y_encoded, num_classes)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_categorical, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    
    # Create model
    print("\nBuilding model...")
    model = create_model(X.shape[1], num_classes)
    model.summary()
    
    # Callbacks
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
    
    # Train model
    print("\nTraining model...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=args.epochs,
        batch_size=args.batch_size,
        callbacks=[early_stopping, reduce_lr],
        verbose=1
    )
    
    # Evaluate model
    print("\nEvaluating model...")
    test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss: {test_loss:.4f}")
    print(f"Test Accuracy: {test_accuracy:.4f}")
    
    # Detailed classification report
    y_pred = model.predict(X_test, verbose=0)
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_test_classes = np.argmax(y_test, axis=1)
    
    from sklearn.metrics import classification_report, confusion_matrix
    
    print("\nClassification Report:")
    print(classification_report(
        y_test_classes, 
        y_pred_classes, 
        target_names=label_encoder.classes_
    ))
    
    print("\nConfusion Matrix:")
    cm = confusion_matrix(y_test_classes, y_pred_classes)
    print(cm)
    
    # Save model
    model_path = os.path.join(args.model_dir, 'isl_model.keras')
    print(f"\nSaving model to {model_path}...")
    model.save(model_path)
    print("✓ Model saved")
    
    # Save labels
    labels_path = os.path.join(args.model_dir, 'labels.npy')
    print(f"Saving labels to {labels_path}...")
    np.save(labels_path, label_encoder.classes_)
    print("✓ Labels saved")
    
    # Plot training history
    plot_path = os.path.join(args.model_dir, 'training_plot.png')
    plot_training_history(history, plot_path)
    
    # Convert to TensorFlow Lite
    print("\nConverting to TensorFlow Lite...")
    converter = keras.saving.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [keras.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    tflite_path = os.path.join(args.model_dir, 'isl_model.tflite')
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    print(f"✓ TFLite model saved to {tflite_path}")
    
    # Check TFLite model size
    tflite_size = os.path.getsize(tflite_path) / 1024
    print(f"  TFLite model size: {tflite_size:.2f} KB")
    
    print("\n=== Training Complete! ===")
    print(f"Final Test Accuracy: {test_accuracy:.2%}")
    print(f"Model: {model_path}")
    print(f"Labels: {labels_path}")
    print(f"TFLite: {tflite_path}")


if __name__ == "__main__":
    main()
