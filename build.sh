#!/usr/bin/env bash
export PATH=$PATH:/usr/local/python3.9.19/bin
export PATH="/opt/render/project/poetry/bin:$PATH"
pip install --upgrade pip
pip install git+https://github.com/benoitc/gunicorn.git

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