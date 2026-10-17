#!/usr/bin/env bash
# ============================================================
# SoilGuard ESP32 MicroPython Flashing Script
# ============================================================
set -e

PORT=${1:-"/dev/ttyUSB0"}
BAUD=${2:-"460800"}
FIRMWARE_BIN=${3:-"esp32-20230426-v1.20.0.bin"}

echo "=== SoilGuard Firmware Deployment ==="
echo "Target Port: $PORT"
echo "Baud Rate:   $BAUD"
echo "Binary:      $FIRMWARE_BIN"

if ! command -v esptool.py &> /dev/null; then
    echo "Error: esptool.py not found. Install via 'pip install esptool'"
    exit 1
fi

echo "[1/3] Erasing flash on ESP32..."
esptool.py --chip esp32 --port "$PORT" erase_flash

echo "[2/3] Writing MicroPython firmware..."
esptool.py --chip esp32 --port "$PORT" --baud "$BAUD" write_flash -z 0x1000 "$FIRMWARE_BIN"

echo "[3/3] Uploading SoilGuard source files..."
ampy --port "$PORT" put src/ /

echo "Deployment complete! Resetting board..."
