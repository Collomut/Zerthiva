param(
    [string]$Port = "COM3",
    [int]$Baud = 460800,
    [string]$FirmwareBin = "esp32-20230426-v1.20.0.bin"
)

Write-Host "=== SoilGuard Firmware Deployment ===" -ForegroundColor Green
Write-Host "Target Port: $Port"
Write-Host "Baud Rate:   $Baud"
Write-Host "Binary:      $FirmwareBin"

if (-not (Get-Command esptool.py -ErrorAction SilentlyContinue)) {
    Write-Error "esptool.py not found. Install via: pip install esptool"
    exit 1
}

Write-Host "[1/3] Erasing ESP32 Flash..." -ForegroundColor Cyan
esptool.py --chip esp32 --port $Port erase_flash

Write-Host "[2/3] Writing MicroPython binary..." -ForegroundColor Cyan
esptool.py --chip esp32 --port $Port --baud $Baud write_flash -z 0x1000 $FirmwareBin

Write-Host "[3/3] Uploading SoilGuard Edge source..." -ForegroundColor Cyan
ampy --port $Port put src/ /

Write-Host "Firmware flashing complete!" -ForegroundColor Green
