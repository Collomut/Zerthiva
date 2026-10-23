# 🌾 Zerthiva — Soil Intelligence System (SIS)

[![CI - Edge Firmware](https://github.com/Collomut/Zerthiva/actions/workflows/firmware-ci.yml/badge.svg)](https://github.com/Collomut/Zerthiva/actions/workflows/firmware-ci.yml)
[![CI - Cloud Backend](https://github.com/Collomut/Zerthiva/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Collomut/Zerthiva/actions/workflows/backend-ci.yml)
[![CI - Regional Dashboard](https://github.com/Collomut/Zerthiva/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/Collomut/Zerthiva/actions/workflows/frontend-ci.yml)
[![Master Technical Dossier](https://img.shields.io/badge/Master_Dossier-58_Sections-059669.svg)](https://collomut.github.io/soilManagement/)
[![3D Soil Simulation](https://img.shields.io/badge/3D_Viewer-WebGL_Simulation-0284c7.svg)](https://collomut.github.io/soilManagement/zerthiva_interactive_3d.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hardware Cost](https://img.shields.io/badge/Hardware%20Cost-%2434.80_BOM-brightgreen)](docs/architecture/hardware_schematic.md)
[![Edge Platform](https://img.shields.io/badge/Firmware-MicroPython%20ESP32-blue)](firmware/)

> **Know Your Soil. Feed Your Field.**  
> An industrial-grade, affordable, solar-powered field intelligence system designed to protect smallholder farms from silent soil salinization, optimize irrigation timing, and calculate precision fertilizer dosage.

---

## 📌 Executive Overview

In irrigated drylands across Sub-Saharan Africa and developing regions, over **20% of irrigated cropland** suffers from insidious salt accumulation. Smallholder farmers typically lack real-time soil visibility, resulting in a vicious cycle: salt deposits build up → plant root osmosis is impeded → farmers mistake stress for drought and apply more salty water or fertilizer → crops collapse.

**Zerthiva** breaks this cycle with an affordable, solar-backed edge node deployed at the crop root zone:
1. **Continuous 15-Minute Sensing:** Measures Soil Salinity (Electrical Conductivity, normalized to 25°C), Volumetric Water Content (VWC%), and Soil Temperature.
2. **On-Device FAO-56 Decision Engine:** Operates 100% offline using peer-reviewed agronomic thresholds to calculate Leaching Requirements (LR) and prevent fertilizer toxicity.
3. **Multi-Tier Alerting:**
   - **Local Sentry:** Instant tri-color RGB pulse (Green = Balanced, Yellow = Irrigate, Red = Salinity Critical).
   - **Farmer Cellular SMS:** Plain-language guidance on basic feature phones (e.g., *"Hold fertilizer! Soil salt high (2.8 dS/m). Flush with 25% extra water."*).
   - **Cloud Telemetry & Web Dashboard:** Aggregates regional soil trends and hypertable telemetry for extension officers and agronomists.

---

---

## 🌐 Complete Platform Ecosystem

Zerthiva is organized into two companion repositories:

1. 💻 **Implementation Stack ([Collomut/Zerthiva](https://github.com/Collomut/Zerthiva)):**
   - **ESP32 Edge Firmware:** MicroPython sensor acquisition, 25°C baseline normalization, and offline FAO-56 decision engine.
   - **Cloud API Gateway:** FastAPI + SQLAlchemy async service for telemetry ingestion, SMS dispatch, and anomaly detection.
   - **Regional Dashboard:** React + Vite + Tailwind CSS console for agricultural extension officers.
   - **Field Node Simulator:** Synthetic telemetry stream generator with realistic diurnal cycles and salt spikes.

2. 📘 **Research Platform & 3D Exhibition ([Collomut/soilManagement](https://github.com/Collomut/soilManagement)):**
   - 🌐 **[Master Technical Dossier (58 Sections & 9 Annexes)](https://collomut.github.io/soilManagement/):** Complete agronomic evidence base, power budgets, Rhoades conversion models, and matched-pair pilot methodology.
   - 🌾 **[Interactive 3D WebGL Soil Intelligence Simulation](https://collomut.github.io/soilManagement/zerthiva_interactive_3d.html):** Cinematic real-time 3D cutaway of crop root-zone electrochemical sensing with PBR soil strata.

---
## 🏛️ System Architecture

```text
               +------------------------------------------------+
               |            Crop Root Zone (-20cm)              |
               |  [Analog EC]   [Capacitive Moist]   [DS18B20]  |
               +-----------------------+------------------------+
                                       |
                                       v
               +------------------------------------------------+
               |          ESP32 Edge Node (Solar / IP65)        |
               |  - MicroPython Runtime                         |
               |  - Temperature Compensation (25°C baseline)    |
               |  - FAO-56 Decision Engine (Offline Logic)       |
               |  - MicroSD 7-Day Rolling CSV Logger            |
               +-----------+----------------------+-------------+
                           |                      |
            [Local Sentry Pulse]         [SIM800L Cellular Modem]
           (Tri-Color RGB Beacon)                 |
                           |             +--------+--------+
                     Farmer in Field     |                 |
                   (Zero Literacy UI)    v                 v
                                  Actionable SMS     JSON Telemetry
                                   (Nokia 105)        (GPRS Uplink)
                                                           |
                                                           v
                                            +-----------------------------+
                                            |   Cloud Gateway (FastAPI)   |
                                            |   TimescaleDB Time-Series   |
                                            |   React Agronomic Dashboard |
                                            +-----------------------------+
```

---

## 🗂️ Repository Directory Structure

```text
Zerthiva/
├── firmware/                       # ESP32 Edge Firmware (MicroPython)
│   ├── src/
│   │   ├── config.py               # Pin definitions, calibration constants, crop profiles
│   │   ├── main.py                 # 15-min RTC deep-sleep orchestrator
│   │   ├── sensors/                # Drivers: EC probe, capacitive moisture, DS18B20 temp
│   │   ├── engine/                 # FAO-56 decision engine & tri-color LED sentry
│   │   ├── storage/                # MicroSD SPI driver & rolling CSV logger
│   │   └── comms/                  # SIM800L cellular modem driver & WiFi client
│   ├── tests/                      # Edge agronomic logic unit tests
│   ├── flash_firmware.sh           # MicroPython flashing script
│   └── requirements-dev.txt
│
├── backend/                        # Cloud Telemetry & Advisory API (FastAPI)
│   ├── app/
│   │   ├── core/                   # Config, security, async database session
│   │   ├── models/                 # SQLAlchemy ORM (Farm, Node, Telemetry, Alert)
│   │   ├── schemas/                # Pydantic v2 validation models
│   │   ├── services/               # SMS gateway, anomaly detection, decision service
│   │   └── api/v1/                 # REST endpoints: /ingest, /farms, /telemetry, /advisory
│   ├── tests/                      # Pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                       # Extension Officer Dashboard (React + Vite + Tailwind)
│   ├── src/
│   │   ├── components/             # StatCard, SalinityChart, MoistureGauge, FarmMap
│   │   ├── pages/                  # Regional Dashboard, FarmDetail, AlertCenter
│   │   ├── services/               # Axios API client with device/user token handling
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── simulator/                      # Synthetic Sensor & Field Emulator
│   ├── mock_field_node.py          # Diurnal cycles, rainfall spikes, salt accumulation
│   ├── run_simulation.py           # Automated telemetry stream generator
│   └── Dockerfile
│
├── docs/                           # Specifications & Schematics
│   ├── architecture/               # Data Flow Diagrams (DFD) & UML diagrams (Mermaid)
│   └── hardware_schematic.md       # Pinout maps, BOM cost table & wiring guide
│
├── ci/workflows/                   # Automated CI/CD Pipelines
│   ├── firmware-ci.yml             # Firmware linting & logic tests
│   ├── backend-ci.yml              # Pytest & backend container validation
│   └── frontend-ci.yml             # React dashboard build verification
│
├── .github/                        # Pull request templates & community guidelines
├── docker-compose.yml              # Local dev stack (PostgreSQL/TimescaleDB, API, UI, Simulator)
├── .env.example
├── LICENSE                         # MIT License
└── README.md
```

---

## ⚡ Quick Start

### 1. Run the Entire Stack via Docker Compose

```bash
# Clone the repository
git clone https://github.com/Collomut/Zerthiva.git
cd Zerthiva

# Copy environment settings
cp .env.example .env

# Spin up TimescaleDB, Backend API, Dashboard, and Synthetic Simulator
docker compose up --build
```
- **Web Dashboard:** `http://localhost:3000`
- **FastAPI Interactive Docs:** `http://localhost:8000/docs`
- **Telemetry Ingest Endpoint:** `http://localhost:8000/api/v1/ingest/telemetry`

---

### 2. Run Cloud Backend Locally

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

---

### 3. Run Field Node Simulator

The simulator streams realistic telemetry (sinusoidal diurnal temp, dry-down curves, salt accumulation) directly to the backend:

```bash
cd simulator
python run_simulation.py --endpoint http://localhost:8000/api/v1/ingest/telemetry --node-id SG-NODE-001 --interval 5
```

---

### 4. Run Edge Firmware Tests

```bash
cd firmware
python -m unittest discover -s tests
```

---

## 🔬 Agronomic Science & FAO-56 Reference

Zerthiva implements peer-reviewed FAO standards for crop salinity management:

$$\text{LR} = \frac{\text{EC}_w}{5 \cdot \text{EC}_e - \text{EC}_w}$$

- $\text{EC}_w$: Electrical conductivity of irrigation water (dS/m)
- $\text{EC}_e$: Crop root-zone salinity threshold before yield decline occurs
- $\text{LR}$: Leaching Requirement (fraction of extra water needed to flush salts below root zone)

| Crop | Safe Salinity Threshold ($\text{EC}_e$) | Yield Decline per dS/m | Refill Moisture (VWC%) | Field Capacity (VWC%) |
| :--- | :---: | :---: | :---: | :---: |
| **Maize** | $1.7\text{ dS/m}$ | $12.0\%$ | $22\%$ | $38\%$ |
| **Tomato** | $2.5\text{ dS/m}$ | $9.9\%$ | $25\%$ | $40\%$ |
| **Rice** | $3.0\text{ dS/m}$ | $12.0\%$ | $35\%$ | $55\%$ |
| **Wheat** | $6.0\text{ dS/m}$ | $7.1\%$ | $20\%$ | $35\%$ |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.