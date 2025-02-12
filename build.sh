#!/usr/bin/env bash
pip install --upgrade pip

# Install system dependencies
sudo apt-get update && sudo apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils

which tesseract
which pdftotext
which pdftoppm

echo "--echoing path START--"
echo $PATH
echo "--echoing path END--"

# Install Python dependencies
pip install -r requirements.txt