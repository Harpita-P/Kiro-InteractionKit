#!/bin/bash

# Kiro InteractionKit Setup Script
# This script helps you get started with Kiro InteractionKit

echo "=================================="
echo "Kiro InteractionKit Setup"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo ""

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo ""

# Test camera
echo "Testing camera access..."
camera_result=$(python -c "import cv2; cap = cv2.VideoCapture(0); success = cap.isOpened(); cap.release(); print('success' if success else 'failed')")

if [ "$camera_result" = "success" ]; then
    echo "✓ Camera accessible"
    echo ""
    echo "=================================="
    echo "Environment configured and camera accessible."
    echo "=================================="
else
    echo "✗ Camera not accessible"
    echo ""
    echo "=================================="
    echo "Environment configured but camera not accessible."
    echo "Please check camera permissions and connections."
    echo "=================================="
fi
