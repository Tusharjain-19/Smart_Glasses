#!/bin/bash

# Start Script for Smart Glasses
# This script activates the virtual environment and runs the deployment script

cd /home/pi/Smart_Glasses

# Activate virtual environment
source venv/bin/activate

# Start the deployment script
python src/deploy_pi.py
