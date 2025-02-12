#!/usr/bin/env bash

pip install --upgrade pip
pip install --force-reinstall gunicorn

# Install system dependencies
apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils

# Install Python dependencies
pip install -r requirements.txt
echo "--echoing path START--"
echo $PATH
echo "--echoing path END--"