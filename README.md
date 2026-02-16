# 🤟 Smart Glasses — Indian Sign Language (ISL) to Speech

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Wearable smart glasses with integrated camera that recognize Indian Sign Language (ISL) in real-time, convert signs to text, then to speech audio via Bluetooth speaker pendant. Helps mute/deaf ISL users communicate seamlessly with hearing people.

![Smart Glasses Demo](docs/images/demo.gif)

---

## 📖 Table of Contents

- [How It Works](#how-it-works)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Hardware Requirements](#hardware-requirements)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Hardware Assembly](#hardware-assembly)
- [ISL Datasets](#isl-datasets)
- [Training Your Own Model](#training-your-own-model)
- [Mobile Web App](#mobile-web-app)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [References](#references)
- [License](#license)

---

## 🔄 How It Works

Complete pipeline from camera to speech:

```
📷 Camera Capture (640×480 @ 30fps)
    ↓
👁️ MediaPipe Hands Detection (21 landmarks × 3 coords × 2 hands = 126 features)
    ↓
🧠 Neural Network Classifier (Dense layers with BatchNorm & Dropout)
    ↓
📝 ISL Sign Text (with confidence threshold & stability buffer)
    ↓
🔊 pyttsx3 Text-to-Speech (espeak backend on Pi)
    ↓
🔵 Bluetooth Speaker Output (via PulseAudio)
```

### Technical Details

1. **Hand Detection**: MediaPipe Hands extracts 21 3D landmarks per hand (x, y, z coordinates)
2. **Feature Extraction**: 126 features total (2 hands × 21 landmarks × 3 coords), normalized relative to wrist
3. **Classification**: Deep neural network with 256→128→64 neurons + regularization
4. **Stability Filter**: Requires 15 consecutive identical predictions before announcing
5. **Cooldown Timer**: Prevents repeated announcements within 3 seconds
6. **TTS Output**: Runs in separate thread to avoid blocking video processing
7. **Bluetooth Audio**: PulseAudio routes speech to paired BT speaker

---

## ✨ Features

- ✅ **Real-time ISL Recognition** — 15-20 FPS on Raspberry Pi Zero 2W
- ✅ **Mobile Web Control Panel** — Pair Bluetooth, configure settings, collect data via phone browser
- ✅ **No Command Line Pairing** — Everything controlled through webapp
- ✅ **Confidence Thresholding** — Only announces high-confidence predictions (default 70%)
- ✅ **Stability Buffer** — Reduces false positives with consecutive frame verification
- ✅ **Customizable Training** — Collect your own ISL signs with included data collection tool
- ✅ **TensorFlow Lite Optimization** — Fast inference on resource-constrained devices
- ✅ **3D Printable Frame** — Complete design specifications included
- ✅ **Battery Powered** — 2-3 hour runtime with 2000mAh LiPo
- ✅ **Bluetooth Speaker Pendant** — Clean audio without glasses vibration

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **SBC** | Raspberry Pi Zero 2W | Main processing unit (quad-core ARM) |
| **Camera** | OV5647 5MP Nano Module | Video capture via CSI interface |
| **Computer Vision** | MediaPipe Hands | Hand landmark detection |
| **ML Framework** | TensorFlow 2.16 + Keras | Model training |
| **Inference** | TensorFlow Lite | Optimized on-device inference |
| **TTS** | pyttsx3 + espeak | Text-to-speech conversion |
| **Web Framework** | Flask 3.0 + Flask-SocketIO | Mobile web interface |
| **Audio Output** | PulseAudio + Bluetooth | Wireless audio to speaker |
| **Languages** | Python 3.9+ | Primary language |
| **Dependencies** | OpenCV, NumPy, scikit-learn | Image processing & ML utilities |

---

## 🔧 Hardware Requirements

### Bill of Materials (BOM) — Budget India Prices

| Component | Model/Specs | Price (INR) | Where to Buy | Why This One |
|-----------|------------|-------------|--------------|--------------|
| **SBC** | Raspberry Pi Zero 2 W (65×30×5mm, 11g) | ₹1,800–2,200 | [Robu.in](https://robu.in), ThinkRobotics | Quad-core ARM, WiFi+BT, tiny form factor, runs TF Lite |
| **Camera** | OV5647 Mini 5MP Nano (8.5×8.5×7mm) | ₹350–500 | [Amazon.in](https://amazon.in), Robu.in | Ultra-compact nano module fits in glasses bridge, 1080p, CSI |
| **CSI Cable** | 15cm FFC 22pin-to-15pin adapter | ₹80–150 | Amazon.in | Essential for Pi Zero mini CSI connector |
| **MicroSD** | SanDisk 32GB Class 10 A1 | ₹350–450 | Amazon.in | Fast boot + model loading, reliable brand |
| **Battery** | 3.7V 2000mAh LiPo (60×35×8mm slim) | ₹250–400 | Robu.in | 2-3hr runtime, lightweight, slim form factor |
| **Charger** | TP4056 USB-C Module (25×19×1mm) | ₹50–80 | Robu.in | Safe LiPo charging with overcharge protection |
| **Boost Converter** | MT3608 Step-Up 3.7V→5V (36×17×14mm) | ₹40–70 | Robu.in | Regulated 5V for Pi from LiPo battery |
| **Speaker** | BT 5.0 Pendant Speaker (any small BT) | ₹250–400 | Amazon.in | Separate pendant = no vibration on glasses, better audio |
| **Power Switch** | SPDT Slide Switch SS12D00 (7×3×3mm) | ₹10–20 | Robu.in | Manual on/off control |
| **Capacitor** | Electrolytic 10µF 16V | ₹5–10 | Robu.in | Smooth power output from boost converter |
| **Misc** | Jumper wires, JST 2-pin, heat shrink | ₹100–200 | Robu.in | Assembly and wiring |
| **Glasses Frame** | 3D Printed (PETG/ABS) | ₹100–300 | Own 3D printer | Custom design houses all components |
| | **TOTAL** | **₹3,385–4,780** | | Complete working system |

### Speaker Placement Philosophy

**Version 1 (Current)**: Bluetooth pendant/neckband speaker
- ✅ No vibration affecting camera stability
- ✅ Better audio quality (larger speaker)
- ✅ Easy to replace/upgrade
- ✅ No additional weight on glasses
- ✅ User can position for optimal hearing

**Version 2 (Future)**: Bone conduction in temple arms
- Would require custom bone conduction transducers
- More complex integration
- Recommended only after V1 is working perfectly

---

## 📁 Project Structure

```
Smart_Glasses/
├── src/
│   ├── collect_data.py      # Data collection script with MediaPipe
│   ├── train_model.py        # Model training with TensorFlow/Keras
│   ├── inference.py          # Real-time inference with TTS (desktop)
│   ├── deploy_pi.py          # Raspberry Pi deployment (TFLite)
│   └── utils.py              # Utility functions (landmarks, models)
├── webapp/
│   ├── app.py                # Flask web app for mobile control
│   ├── templates/            # HTML templates
│   │   ├── base.html         # Base template with navigation
│   │   ├── index.html        # Dashboard (status, start/stop)
│   │   ├── bluetooth.html    # Bluetooth pairing interface
│   │   ├── settings.html     # Configuration settings
│   │   ├── collect.html      # Data collection control
│   │   ├── train.html        # Training control
│   │   └── logs.html         # Live logs viewer
│   └── static/
│       └── style.css         # Mobile-responsive dark theme CSS
├── docs/
│   ├── HARDWARE_GUIDE.md     # Detailed hardware assembly guide
│   ├── ML_TRAINING_GUIDE.md  # Beginner-friendly ML guide
│   └── WEBAPP_GUIDE.md       # Web app usage guide
├── scripts/
│   ├── setup_pi.sh           # Complete Pi setup script
│   └── start_glasses.sh      # Start script for deployment
├── models/                    # Trained models (gitignored)
│   ├── isl_model.keras       # Full Keras model
│   ├── isl_model.tflite      # TFLite model for Pi
│   ├── labels.npy            # Label list
│   └── training_plot.png     # Training curves
├── data/                      # Training data CSVs (gitignored)
│   └── SignName.csv          # One CSV per sign class
├── logs/                      # Application logs (gitignored)
│   └── smart_glasses.log     # Main log file
├── config.json               # Configuration file
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore patterns
├── LICENSE                  # MIT License
└── README.md               # This file
```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Tusharjain-19/Smart_Glasses.git
cd Smart_Glasses
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Collect Training Data

Collect samples for each ISL sign you want to recognize:

```bash
python src/collect_data.py --sign "Hello" --samples 200
python src/collect_data.py --sign "Thanks" --samples 200
python src/collect_data.py --sign "A" --samples 200
# ... collect more signs
```

**Instructions during collection:**
- Press **S** to start/stop collecting
- Show the sign clearly to webcam
- Vary angles, distances, lighting
- Press **Q** to quit

### 4. Train Model

```bash
python src/train_model.py
```

This will:
- Load all collected CSVs from `data/`
- Train a neural network
- Save model to `models/isl_model.keras`
- Save TFLite model to `models/isl_model.tflite`
- Save labels to `models/labels.npy`
- Generate training plot

### 5. Test Inference (Desktop)

```bash
python src/inference.py
```

**Controls:**
- Show ISL signs to webcam
- Press **R** to reset stability buffer
- Press **Q** to quit

### 6. Deploy to Raspberry Pi

See [Deployment](#deployment) section below.

---

## 🔩 Hardware Assembly

See detailed guide: [docs/HARDWARE_GUIDE.md](docs/HARDWARE_GUIDE.md)

**Quick Overview:**

1. **3D Print Glasses Frame** (PETG, 0.15mm layers, 50% infill)
2. **Mount Camera** in bridge recess, route CSI cable to right temple
3. **Install Pi Zero** in right temple cavity
4. **Wire Power Circuit** in left temple:
   - LiPo → TP4056 (charging) → MT3608 (5V boost) → Switch → Pi
5. **Connect Components** via GPIO
6. **Close Access Panels** (snap-fit)
7. **Pair Bluetooth Speaker** via webapp

**Total Assembly Time:** 2-3 hours

---

## 📚 ISL Datasets

If you don't want to collect your own data, use these public datasets:

| Dataset | Signs | Samples | Link |
|---------|-------|---------|------|
| **Mendeley ISL** | 26 alphabets | 52,000+ | [Mendeley](https://data.mendeley.com/datasets/n34wm8sb3x/1) |
| **IEEE DataPort ISL Fingerspelling** | 35 fingerspelling | 20,000+ | [IEEE](https://ieee-dataport.org/documents/isl-fingerspelling-image-dataset) |
| **RealSign ISL** | Multiple words | 1000+ videos | [GitHub](https://github.com/RealSign62/RealSign-Indian-Sign-Language-Dataset) |
| **Kaggle ISL Landmarks** | Multiple | Pre-extracted | [Kaggle](https://www.kaggle.com/datasets/eraakash/indian-sign-language-hand-landmarks-dataset) |
| **IIITA-ROBITA** | Research dataset | Various | [ROBITA](https://robita.iiita.ac.in/dataset.php) |

**Note:** These datasets may need preprocessing to extract MediaPipe landmarks. Use `collect_data.py` for best results.

---

## 🎓 Training Your Own Model

See detailed guide: [docs/ML_TRAINING_GUIDE.md](docs/ML_TRAINING_GUIDE.md)

**Tips for Better Accuracy:**

1. **Collect More Data** (300-500 samples per sign)
2. **Vary Conditions**:
   - Different lighting (bright, dim, outdoor)
   - Different backgrounds
   - Different hand positions/angles
   - Different distances from camera
3. **Balance Classes** (equal samples per sign)
4. **Use Data Augmentation** (rotate, flip, scale landmarks)
5. **Tune Hyperparameters**:
   - Adjust confidence threshold (0.6-0.8)
   - Adjust stability frames (10-20)
   - Try different network architectures

**Model Performance Benchmarks:**

| Hardware | Inference Time | FPS | Power |
|----------|----------------|-----|-------|
| Desktop (CPU) | ~15ms | 60+ | N/A |
| Raspberry Pi 4 | ~40ms | 25 | 3-5W |
| Pi Zero 2W (TFLite) | ~60ms | 15-18 | 1-2W |

---

## 📱 Mobile Web App

Access from your phone on the same WiFi network as the Pi:

```
http://raspberrypi.local:5000
```

Or use the Pi's IP address:

```
http://192.168.1.xxx:5000
```

### Features:

- **Dashboard**: View status, current detected sign, FPS, start/stop inference
- **Bluetooth**: Scan, pair, connect Bluetooth speaker (no command line!)
- **Settings**: Adjust confidence, stability, cooldown, speech rate/volume
- **Collect**: Start/stop data collection remotely
- **Train**: Trigger model training, monitor progress
- **Logs**: View live system logs

See full guide: [docs/WEBAPP_GUIDE.md](docs/WEBAPP_GUIDE.md)

---

## 🚀 Deployment

### Raspberry Pi Setup

1. **Flash Raspberry Pi OS Lite** to microSD (64-bit recommended)
2. **Enable SSH** and WiFi (via `boot` partition configs)
3. **Boot Pi** and SSH in: `ssh pi@raspberrypi.local`
4. **Clone repository**:
   ```bash
   git clone https://github.com/Tusharjain-19/Smart_Glasses.git
   cd Smart_Glasses
   ```
5. **Run setup script**:
   ```bash
   chmod +x scripts/setup_pi.sh
   sudo ./scripts/setup_pi.sh
   ```
   This installs all dependencies, sets up services, configures Bluetooth/audio.

6. **Copy trained models** to Pi:
   ```bash
   scp models/* pi@raspberrypi.local:~/Smart_Glasses/models/
   ```

7. **Start web app**:
   ```bash
   sudo systemctl start smart-glasses-webapp
   ```

8. **Access webapp from phone**: `http://raspberrypi.local:5000`

9. **Pair Bluetooth speaker** via webapp

10. **Start inference** via webapp or:
    ```bash
    python src/deploy_pi.py
    ```

### Auto-Start on Boot

Enable services to start automatically:

```bash
sudo systemctl enable smart-glasses-webapp.service
sudo systemctl enable smart-glasses.service
```

---

## 🗺️ Roadmap

### Phase 1: Alphabets ✅ (Current)
- ✅ A-Z ISL fingerspelling recognition
- ✅ Desktop inference with TTS
- ✅ Basic model training

### Phase 2: Numbers 🔄 (In Progress)
- 🔄 0-9 digit recognition
- 🔄 Combined alphabet + number model

### Phase 3: Words 📋 (Planned)
- Use LSTM for temporal sequence recognition
- Common ISL words ("Hello", "Thanks", "Sorry", etc.)
- Larger vocabulary (100-200 words)

### Phase 4: Sentences 🚀 (Future)
- Multi-word sentence recognition
- Grammar rules for ISL
- Context-aware predictions

### Phase 5: TFLite Optimization ⚡ (Ongoing)
- ✅ Basic TFLite conversion
- Model quantization (INT8)
- Further latency reduction (<30ms)

### Phase 6: 3D Printed Frame 🖨️ (Ready)
- ✅ Complete design specifications
- Print and assemble
- Iterate on ergonomics

### Phase 7: Mobile Control ✅ (Complete)
- ✅ Flask web app
- ✅ Bluetooth pairing via webapp
- ✅ Settings management
- ✅ Remote training trigger

### Phase 8: Cloud Sync ☁️ (Future)
- Cloud model training
- Shared sign database
- Multi-user learning

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Areas for Contribution:

- 🗃️ **ISL Datasets**: Collect and share more ISL sign data
- 🧠 **Model Improvements**: Better architectures, accuracy
- 🎨 **UI/UX**: Improve web app interface
- 📖 **Documentation**: Tutorials, translations
- 🔧 **Hardware**: Alternative component recommendations
- 🐛 **Bug Fixes**: Report and fix issues

### Code Style:

- Follow PEP 8 for Python
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

---

## 📚 References

This project builds upon excellent prior work:

- **MediaPipe Hands**: [Google MediaPipe](https://google.github.io/mediapipe/solutions/hands)
- **Sign Language Detection**: [dishak23/SignLanguage-Detection](https://github.com/dishak23/SignLanguage-Detection)
- **Hand Gesture Recognition**: [kinivi/hand-gesture-recognition-mediapipe](https://github.com/kinivi/hand-gesture-recognition-mediapipe)
- **Raspberry Pi SLT Glasses**: [Research project on wearable SLT](https://www.researchgate.net)
- **ISL Research**: Indian Sign Language Research and Training Centre (ISLRTC)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/Tusharjain-19/Smart_Glasses/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Tusharjain-19/Smart_Glasses/discussions)
- **Email**: tusharjain19@example.com

---

## 🌟 Acknowledgments

- Google MediaPipe team for excellent hand tracking
- Indian Sign Language community for inspiration
- Open source contributors worldwide
- Raspberry Pi Foundation

---

**Made with ❤️ for the deaf and hard-of-hearing community**

_Empowering communication through technology_ 🤟