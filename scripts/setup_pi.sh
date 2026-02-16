#!/bin/bash

# Raspberry Pi Setup Script for Smart Glasses
# This script sets up all required software and services

set -e

echo "============================================"
echo "Smart Glasses - Raspberry Pi Setup"
echo "============================================"

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz0b \
    libwebp6 \
    libjasper1 \
    libilmbase23 \
    libopenexr23 \
    libgstreamer1.0-0 \
    libavcodec58 \
    libavformat58 \
    libswscale5 \
    libqtgui4 \
    libqt4-test \
    libportaudio2 \
    espeak \
    pulseaudio \
    pulseaudio-module-bluetooth \
    bluez \
    bluez-tools

# Enable camera interface
echo "Enabling camera interface..."
sudo raspi-config nonint do_camera 0

# Setup PulseAudio for Bluetooth audio
echo "Configuring PulseAudio..."
if ! grep -q "load-module module-bluetooth-discover" /etc/pulse/system.pa; then
    echo "load-module module-bluetooth-discover" | sudo tee -a /etc/pulse/system.pa
fi

# Start PulseAudio
pulseaudio --start || true

# Create project directory structure
echo "Setting up project directory..."
cd /home/pi

if [ ! -d "Smart_Glasses" ]; then
    echo "Project directory not found. Please clone the repository first."
    echo "Run: git clone <repository-url> Smart_Glasses"
    exit 1
fi

cd Smart_Glasses

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install picamera2 (Pi-specific)
echo "Installing picamera2..."
pip install picamera2

# Create necessary directories
echo "Creating directories..."
mkdir -p models data logs

# Set permissions
chmod +x scripts/*.sh

# Create systemd service for auto-start
echo "Creating systemd service..."
sudo tee /etc/systemd/system/smart-glasses.service > /dev/null <<EOF
[Unit]
Description=Smart Glasses ISL Recognition
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Smart_Glasses
ExecStart=/home/pi/Smart_Glasses/scripts/start_glasses.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for web app
echo "Creating web app service..."
sudo tee /etc/systemd/system/smart-glasses-webapp.service > /dev/null <<EOF
[Unit]
Description=Smart Glasses Web App
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Smart_Glasses
ExecStart=/home/pi/Smart_Glasses/venv/bin/python webapp/app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Enable services (but don't start yet)
echo "Enabling services..."
sudo systemctl enable smart-glasses-webapp.service

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Collect training data: python src/collect_data.py --sign <SignName> --samples 200"
echo "2. Train model: python src/train_model.py"
echo "3. Start web app: sudo systemctl start smart-glasses-webapp"
echo "4. Access web app: http://raspberrypi.local:5000"
echo "5. Pair Bluetooth speaker via web app"
echo "6. Start inference: Use web app or run python src/deploy_pi.py"
echo ""
echo "To enable auto-start on boot:"
echo "sudo systemctl enable smart-glasses.service"
echo ""
