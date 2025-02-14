#!/usr/bin/env bash
pip install --upgrade pip

# Install system dependencies
apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils

which tesseract
which pdftotext
which pdftoppm

echo "=========================installing poppler-utils"

apt-get install poppler-utils

echo "--echoing path START--"
echo $PATH
echo "--echoing path END--"

ls

echo "--------------------"

pwd 

# Install Python dependencies
pip install -r requirements.txt