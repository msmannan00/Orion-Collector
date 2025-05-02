#!/bin/bash

set -e

echo "🔄 Updating package list..."
sudo apt-get update

echo "📦 Installing system dependencies (Playwright, Python, etc.)..."
sudo apt-get install -y \
    python3.12-venv \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libgtk-3-0t64 \
    libdrm2 \
    libasound2t64 \
    libpangocairo-1.0-0 \
    libgbm1 \
    libxcb1 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libpci3 \
    libx11-xcb1 \
    fonts-liberation \
    libappindicator3-1 \
    libnss3-tools \
    xdg-utils \
    wget \
    curl \
    unzip \
    ca-certificates \
    redis-server \
    gnupg \
    software-properties-common

echo "✅ System dependencies and Redis installed."

# --- Python venv setup ---
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 not found. Please install it before continuing."
    exit 1
fi

echo "🐍 Creating Python virtual environment..."
python3.12 -m venv venv
source venv/bin/activate

echo "📦 Upgrading pip..."
pip install --upgrade pip

echo "📜 Installing Python dependencies..."
pip install -r requirements.txt

echo "🎭 Installing Playwright browser (Chromium)..."
playwright install chromium
playwright install firefox

echo "✅ Setup complete! Redis, Python venv, and Playwright are ready to go."
