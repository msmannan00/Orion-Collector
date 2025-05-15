#!/bin/bash

set -e

RAW_DIR="raw"
MODEL_ZIP_NAME="ru_en_model.zip"
EXTRACTED_DIR_NAME="translate-en_ru-1_9"
MODEL_URL="https://drive.usercontent.google.com/download?id=1S20Mr4S0uaIr-HAMtFpeZ_eaQEIOd8x2&export=download&authuser=0&confirm=t&uuid=f267de8b-6613-482b-b207-8e407b81ff3d&at=ALoNOgnOI36I_sU3TLvccOwQrYCC%3A1746775757150"

echo "[INFO] Installing required Python packages..."
pip install --upgrade pip
pip install argostranslate requests

echo "[INFO] Preparing directories..."
mkdir -p "$RAW_DIR"
ZIP_PATH="$RAW_DIR/$MODEL_ZIP_NAME"
MODEL_DIR="$RAW_DIR/$EXTRACTED_DIR_NAME"

if [ -f "$ZIP_PATH" ]; then
    echo "[INFO] Removing old ZIP file..."
    rm "$ZIP_PATH"
fi

if [ -d "$MODEL_DIR" ]; then
    echo "[INFO] Removing old model directory..."
    rm -rf "$MODEL_DIR"
fi

echo "[INFO] Downloading translation model..."
curl -L -o "$ZIP_PATH" "$MODEL_URL"

echo "[INFO] Extracting model..."
unzip "$ZIP_PATH" -d "$RAW_DIR"
rm "$ZIP_PATH"

echo "[INFO] Installing Argos model if available..."
FOUND=0
for FILE in $(find "$RAW_DIR" -type f -name "*.argosmodel"); do
    argos-translate install "$FILE"
    echo "[INFO] Installed: $FILE"
    FOUND=1
done

if [ "$FOUND" -eq 0 ]; then
    echo "[INFO] No .argosmodel files found. Assuming structured model already available."
fi

echo "[DONE] Argos Translate setup complete."
