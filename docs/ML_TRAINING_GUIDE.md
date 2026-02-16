# 🎓 Machine Learning Training Guide

Beginner-friendly guide to training your ISL recognition model.

---

## 📚 What is Machine Learning?

Think of machine learning like teaching a child to recognize objects:

1. **Show examples**: You show a child many pictures of cats and say "cat"
2. **Child learns patterns**: They notice cats have pointy ears, whiskers, four legs
3. **Child recognizes new cats**: Even cats they've never seen before
4. **Correction**: If they call a dog "cat," you correct them and they learn

Our ISL model works the same way:
- **Examples**: Hand landmark positions for each sign
- **Patterns**: Unique finger/hand positions for each sign
- **Recognition**: Identifies signs it's never seen before
- **Correction**: Training with more data improves accuracy

---

## 🤔 Why MediaPipe Landmarks?

### Option 1: Raw Images (❌ Not Used)
```
[640x480 pixel image] = 307,200 numbers to process
↓
• Slow (lots of data)
• Position-dependent (sign must be in exact same spot)
• Lighting-dependent (won't work in different lighting)
• Large model (megabytes)
```

### Option 2: MediaPipe Landmarks (✅ What We Use)
```
[21 hand positions × 2 hands × 3 coordinates] = 126 numbers
↓
• Fast (1% of the data)
• Position-invariant (works anywhere in frame)
• Lighting-invariant (works in any lighting)
• Tiny model (kilobytes)
```

**Analogy:** Instead of storing full photographs of people, we store their height, weight, and age. Much less data, but still enough to identify them!

---

## 🎯 The Complete Pipeline Explained

### Step 1: Data Collection (You Do This)

```python
# What happens when you run collect_data.py:

1. Open webcam
2. Show ISL sign to camera
3. MediaPipe detects hands and extracts 21 landmarks per hand
   
   Landmarks = [
       [x, y, z],  # Wrist
       [x, y, z],  # Thumb base
       [x, y, z],  # Thumb tip
       # ... 18 more landmarks
   ]
   
4. Save landmarks to CSV file: "SignName.csv"
5. Repeat 200+ times for each sign
```

**What's Saved:**
```csv
h0_l0_x, h0_l0_y, h0_l0_z, h0_l1_x, ... (126 columns)
0.452,   0.678,   0.012,   0.489,  ... (Sample 1)
0.441,   0.683,   0.015,   0.492,  ... (Sample 2)
...
```

Each row = one frame of hand landmarks
Each file = one sign class

### Step 2: Normalization (Automatic)

Raw landmarks are absolute positions on screen. We normalize them relative to the wrist:

**Before Normalization:**
```
Wrist:      (0.5, 0.5, 0.0)
Index tip:  (0.6, 0.3, 0.0)
```

**After Normalization:**
```
Wrist:      (0.0, 0.0, 0.0)  ← Origin point
Index tip:  (0.1, -0.2, 0.0) ← Relative to wrist
```

**Why?** So the sign looks the same whether your hand is:
- On the left or right side of frame
- Close to camera or far away
- Moving around

### Step 3: Model Training

```
Input Layer (126 features)
    ↓
Dense Layer (256 neurons) + ReLU activation
    ↓
Batch Normalization (stabilizes learning)
    ↓
Dropout 30% (prevents overfitting)
    ↓
Dense Layer (128 neurons) + ReLU
    ↓
Batch Normalization
    ↓
Dropout 30%
    ↓
Dense Layer (64 neurons) + ReLU
    ↓
Dropout 20%
    ↓
Output Layer (number of signs) + Softmax
    ↓
Probabilities: [Hello: 0.89, Thanks: 0.05, Sorry: 0.03, ...]
```

**What Each Part Does:**

- **Dense Layer**: Learns patterns in the data
- **ReLU Activation**: "Turns on" neurons that detect patterns
- **Batch Normalization**: Keeps numbers in reasonable range (faster learning)
- **Dropout**: Randomly "turns off" neurons during training (prevents memorization)
- **Softmax**: Converts scores to probabilities that sum to 100%

### Step 4: Inference (Real-Time Recognition)

```
1. Camera captures frame
2. MediaPipe extracts landmarks → [126 numbers]
3. Normalize landmarks relative to wrist
4. Feed into model
5. Model outputs probabilities for each sign
6. Pick sign with highest probability (if > 70% confident)
7. Check stability buffer (15 consecutive same predictions)
8. If stable + not in cooldown → announce via TTS
```

---

## 📊 Data Collection Best Practices

### How Much Data?

| Scenario | Samples per Sign | Accuracy |
|----------|-----------------|----------|
| **Testing** | 50-100 | ~60-70% |
| **Good** | 200-300 | ~80-90% |
| **Great** | 500-1000 | ~90-95% |
| **Excellent** | 2000+ | ~95-99% |

**Recommendation:** Start with 200, add more if accuracy is low.

### Variation is Key!

For each sign, collect samples with:

✅ **Different Angles:**
- Facing camera straight
- Hand rotated left/right 30°
- Hand tilted up/down 20°

✅ **Different Distances:**
- Close to camera (hand fills frame)
- Medium distance (comfortable arm extension)
- Far from camera (arm fully extended)

✅ **Different Positions:**
- Left side of frame
- Center of frame
- Right side of frame
- High/low in frame

✅ **Different Lighting:**
- Bright room
- Dim lighting
- Natural window light
- Overhead lights

✅ **Different Backgrounds:**
- Plain wall
- Busy background
- Dark background
- Light background

❌ **What NOT to Do:**
- Collect all 200 samples in one continuous recording (too similar)
- Use only one hand position
- Same lighting/background for all samples
- Signs too fast or blurry

### Pro Tips:

1. **Take breaks** between batches (vary your hand position naturally)
2. **Move around** the room between collections
3. **Try tomorrow** with different clothes/lighting
4. **Get others to help** (if your model works for multiple people, even better!)
5. **Clean data** — delete corrupted samples (where MediaPipe failed to detect hands)

---

## 🧠 Understanding the Training Process

### Training vs Testing Data

We split data 80/20:
- **80% Training**: Model learns from these samples
- **20% Testing**: Model never sees these during training (measures real-world performance)

**Why?** Imagine studying for an exam:
- Training data = practice problems you study
- Test data = actual exam questions
- If you memorize answers to practice problems, you might fail the real exam!

### Loss and Accuracy

**Loss** = How wrong the model is
- High loss (2.5) = Model is very confused
- Low loss (0.1) = Model is very confident
- **Goal:** Minimize loss

**Accuracy** = Percentage of correct predictions
- 50% = Model guessing randomly
- 90% = Model correct 9 out of 10 times
- **Goal:** Maximize accuracy

### Training Curve Example

```
Epoch 1:  Loss: 2.30  Accuracy: 15%  ← Model just started, random guessing
Epoch 10: Loss: 0.85  Accuracy: 75%  ← Learning patterns
Epoch 20: Loss: 0.35  Accuracy: 88%  ← Getting better
Epoch 30: Loss: 0.18  Accuracy: 93%  ← Nearly converged
Epoch 40: Loss: 0.15  Accuracy: 94%  ← Plateau (stopped improving)
```

**Early Stopping:** Training stops automatically if validation loss doesn't improve for 15 epochs.

### Overfitting vs Underfitting

**Underfitting (Model too simple):**
```
Training Accuracy: 60%
Testing Accuracy:  55%
→ Model can't learn patterns (both low)
→ Solution: Add more layers, train longer
```

**Good Fit:**
```
Training Accuracy: 92%
Testing Accuracy:  90%
→ Model learned patterns well
→ Small gap is normal (2-5%)
```

**Overfitting (Model memorized training data):**
```
Training Accuracy: 99%
Testing Accuracy:  70%
→ Model memorized instead of learning
→ Solution: More data, more dropout, less training
```

Our model uses **Dropout** and **Early Stopping** to prevent overfitting.

---

## 🚀 Step-by-Step Training

### 1. Collect Data for Multiple Signs

```bash
# Collect 200 samples for each sign
python src/collect_data.py --sign "Hello" --samples 200
python src/collect_data.py --sign "Thanks" --samples 200
python src/collect_data.py --sign "Sorry" --samples 200
python src/collect_data.py --sign "Please" --samples 200
python src/collect_data.py --sign "A" --samples 200
# ... etc
```

**Minimum:** 3 signs  
**Recommended:** 10-20 signs  
**Advanced:** 50+ signs

### 2. Verify Data

Check `data/` directory:
```bash
ls -lh data/

Hello.csv   (200 lines + header)
Thanks.csv  (200 lines + header)
Sorry.csv   (200 lines + header)
...
```

Each file should have 201 lines (1 header + 200 samples).

### 3. Run Training

```bash
python src/train_model.py
```

**What happens:**
```
1. Loads all CSVs from data/
2. Combines into single dataset
3. Shuffles and splits 80/20
4. Creates neural network
5. Trains for up to 100 epochs (usually stops around 30-50)
6. Saves best model to models/isl_model.keras
7. Converts to TFLite for Pi
8. Generates training plot
```

**Training Output:**
```
=== ISL Model Training ===

Loading data...
Found 5 sign classes:
  - Hello: 200 samples
  - Thanks: 200 samples
  - Sorry: 200 samples
  - Please: 200 samples
  - A: 200 samples

Total samples: 1000
Features per sample: 126

Training samples: 800
Testing samples: 200

Building model...
Model: "sequential"
_________________________________________________________________
 Layer (type)                Output Shape              Param #   
=================================================================
 dense (Dense)               (None, 256)               32512     
 batch_normalization (Batch  (None, 256)               1024      
 dropout (Dropout)           (None, 256)               0         
 dense_1 (Dense)             (None, 128)               32896     
 batch_normalization_1       (None, 128)               512       
 dropout_1 (Dropout)         (None, 128)               0         
 dense_2 (Dense)             (None, 64)                8256      
 dropout_2 (Dropout)         (None, 64)                0         
 dense_3 (Dense)             (None, 5)                 325       
=================================================================
Total params: 75,525
Trainable params: 74,757
Non-trainable params: 768
_________________________________________________________________

Training model...
Epoch 1/100
25/25 [==============================] - 2s 50ms/step - loss: 1.4523 - accuracy: 0.4250 - val_loss: 1.2134 - val_accuracy: 0.5650
...
Epoch 35/100
25/25 [==============================] - 1s 25ms/step - loss: 0.0845 - accuracy: 0.9650 - val_loss: 0.1234 - val_accuracy: 0.9400

Early stopping triggered!

Final Test Accuracy: 94.00%
✓ Model saved to models/isl_model.keras
✓ TFLite model saved to models/isl_model.tflite (49.23 KB)
```

### 4. Review Results

**Classification Report:**
```
              precision    recall  f1-score   support

       Hello       0.95      0.93      0.94        40
      Thanks       0.92      0.95      0.93        40
       Sorry       0.94      0.92      0.93        40
      Please       0.95      0.95      0.95        40
           A       0.93      0.95      0.94        40

    accuracy                           0.94       200
   macro avg       0.94      0.94      0.94       200
weighted avg       0.94      0.94      0.94       200
```

**What these mean:**
- **Precision**: When model says "Hello", how often is it actually "Hello"? (95%)
- **Recall**: Of all actual "Hello" signs, how many did model detect? (93%)
- **F1-Score**: Average of precision and recall (94%)
- **Support**: Number of test samples for that sign (40)

**Confusion Matrix:**
```
         Hello  Thanks  Sorry  Please   A
Hello      37      1      0       1     1
Thanks      1     38      0       1     0
Sorry       0      0     37       2     1
Please      0      1      1      38     0
A           0      1      0       0    39
```

**How to read:**
- Row = actual sign
- Column = predicted sign
- Diagonal = correct predictions
- Off-diagonal = mistakes

Example: "Hello" was correctly predicted 37 times, but confused with "Thanks" once, "Please" once, and "A" once.

### 5. View Training Plot

Open `models/training_plot.png`:
- Left graph: Accuracy over epochs
- Right graph: Loss over epochs
- Blue line: Training
- Orange line: Validation

**Good plot:**
- Both accuracy lines increasing
- Both loss lines decreasing
- Small gap between training and validation

**Bad plot (overfitting):**
- Training accuracy very high (>98%)
- Validation accuracy plateaus or decreases
- Large gap between lines

---

## 🎯 Improving Accuracy

### If Accuracy is Low (< 80%)

**1. Collect More Data**
```bash
# Add 200 more samples to each sign
python src/collect_data.py --sign "Hello" --samples 200
# Repeat for all signs
```

**2. Check Data Quality**
- Open CSVs in Excel/LibreOffice
- Look for rows with many zeros (failed detection)
- Delete bad rows
- Re-train

**3. Balance Classes**
- Ensure all signs have similar sample counts
- If "Hello" has 500 samples and "Thanks" has 50, model will bias toward "Hello"

**4. Increase Model Complexity**
Edit `src/train_model.py`:
```python
# Change layer sizes:
layers.Dense(512, activation='relu'),  # Was 256
layers.Dense(256, activation='relu'),  # Was 128
layers.Dense(128, activation='relu'),  # Was 64
```

**5. Train Longer**
```bash
python src/train_model.py --epochs 200  # Default is 100
```

### If Signs are Confused

**Problem:** Model confuses "A" and "E" (similar hand shapes)

**Solution:**
1. Collect more samples emphasizing the difference
2. For "A", emphasize closed fist
3. For "E", emphasize spread fingers
4. Add more variation in angles

### If One Sign is Always Wrong

**Problem:** "Sorry" has 30% accuracy, others have 90%

**Solution:**
1. Check "Sorry" CSV for corrupt data
2. Collect 2x more "Sorry" samples
3. Ensure "Sorry" sign is performed correctly and consistently

---

## ⚡ TensorFlow Lite Conversion

After training, model is automatically converted to TFLite for Raspberry Pi.

**Why TFLite?**
```
Keras Model (.keras):
- Size: 300 KB
- Inference time: 60ms on Pi
- Memory: 150 MB

TFLite Model (.tflite):
- Size: 50 KB (6x smaller)
- Inference time: 35ms on Pi (1.7x faster)
- Memory: 30 MB (5x less)
```

**Quantization (Optional, Advanced):**

For even smaller/faster model:

Edit `src/train_model.py`:
```python
# After training, add:
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]  # or tf.int8
```

**Trade-off:**
- INT8: 4x smaller, 2x faster, -1% accuracy
- FLOAT16: 2x smaller, 1.5x faster, -0.1% accuracy

---

## 🔍 Common Training Errors and Fixes

### Error: "No CSV files found in data/"
**Cause:** Haven't collected any data yet  
**Fix:** Run `collect_data.py` first

### Error: "ValueError: not enough values to unpack"
**Cause:** CSV files have wrong format (manual editing?)  
**Fix:** Delete corrupted CSVs, re-collect data

### Error: "MemoryError" or "Killed"
**Cause:** Not enough RAM (8GB+ recommended for training)  
**Fix:** 
- Use smaller batch size: `--batch_size 16`
- Train on desktop, not Pi
- Close other programs

### Error: "Accuracy stuck at 20%"
**Cause:** Not enough data or data too similar  
**Fix:** Collect more varied samples

### Error: "Loss is NaN"
**Cause:** Learning rate too high or bad data  
**Fix:**
- Check for corrupted data (zeros, infinities)
- Restart training
- Lower learning rate in model definition

---

## 📱 Testing Your Model

### Desktop Testing

```bash
python src/inference.py
```

Show signs to webcam and verify:
- ✅ Correct sign detected
- ✅ Confidence > 70%
- ✅ Stability buffer fills (15 frames)
- ✅ TTS announces sign
- ✅ Cooldown prevents repeats

### Raspberry Pi Testing

```bash
python src/deploy_pi.py
```

Check:
- ✅ FPS > 10 (preferably 15+)
- ✅ No lag or freezing
- ✅ Bluetooth audio works
- ✅ Low latency (<1 second from sign to speech)

### Stress Testing

Try to break the model:
- Very fast signs
- Partial hand in frame
- Multiple people's hands
- Extreme angles
- Low lighting
- Moving around

**Goal:** 85%+ accuracy in real-world conditions

---

## 🎓 Next Steps

Once you have a working model:

1. **Fine-tune threshold** in `config.json`:
   - Lower (0.6) = more detections, more false positives
   - Higher (0.8) = fewer false positives, might miss some signs

2. **Adjust stability** in `config.json`:
   - Fewer frames (10) = faster response, less stable
   - More frames (20) = slower response, very stable

3. **Collect more signs** — build up to 50+ signs

4. **Try temporal models (LSTM)** for sign sequences and sentences

5. **Share your dataset** with the community!

---

## 📚 Additional Resources

- **TensorFlow Tutorials**: https://www.tensorflow.org/tutorials
- **MediaPipe Hands**: https://google.github.io/mediapipe/solutions/hands.html
- **Neural Networks Explained**: https://www.3blue1brown.com/neural-networks
- **ISL Dictionary**: https://indiansignlanguage.org/

---

**Questions?** Open an issue on GitHub!

**Remember:** Machine learning is iterative. Don't expect 99% accuracy on first try. Keep improving your data and model! 🚀
