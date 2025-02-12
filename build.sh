#!/usr/bin/env bash
pip install --upgrade pip

# Install system dependencies
apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils

# Install Python dependencies
pip install -r requirements.txt