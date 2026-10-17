## 🌾 SoilGuard Pull Request

### Summary of Changes
<!-- Provide a clear, concise overview of what has been implemented or resolved -->

### Subsystems Affected
- [ ] `firmware/` (ESP32 MicroPython, Sensor Drivers, RTC Deep Sleep)
- [ ] `backend/` (FastAPI Endpoints, TimescaleDB, SMS Gateway, Auth)
- [ ] `frontend/` (React Dashboard, Agronomic Visualizers, Sentry UI)
- [ ] `simulator/` (Synthetic Sensor Node, Field Emulation)
- [ ] `docs/` (Architecture, DFDs, UMLs, Hardware Schematics)
- [ ] CI/CD or Docker Infrastructure

### Verification & Testing
<!-- Describe the automated or manual tests performed to confirm feasibility -->
- [ ] Firmware unit tests pass (`python -m unittest discover -s firmware/tests`)
- [ ] Backend tests pass (`pytest backend/tests`)
- [ ] Frontend builds cleanly (`npm run build`)
- [ ] Tested against synthetic telemetry stream
- [ ] Verified FAO-56 decision calculation accuracy

### Checklist
- [ ] Code adheres to project style guidelines
- [ ] Documentation updated to reflect changes
- [ ] No sensitive credentials or secrets committed
