"""
Zerthiva Prototype One-Click Launcher
Starts the FastAPI cloud backend, launches the synthetic field simulator,
and opens the interactive agronomic dashboard prototype in your default web browser.
"""

import sys
import os
import time
import webbrowser
import subprocess

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(base_dir, "backend")
    dashboard_html = os.path.join(base_dir, "dashboard_prototype.html")

    print("=" * 65)
    print("🌾 Zerthiva — Interactive Working Prototype Launcher")
    print("=" * 65)
    print("1. Starting FastAPI Cloud Backend on http://127.0.0.1:8000 ...")

    env = os.environ.copy()
    env["PYTHONPATH"] = backend_dir

    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8000", "--host", "127.0.0.1"],
        cwd=backend_dir,
        env=env
    )

    time.sleep(1.5)

    print("2. Opening Interactive Working Dashboard in default browser...")
    webbrowser.open(f"file://{dashboard_html}")

    print("\n" + "=" * 65)
    print("✅ Zerthiva Prototype is RUNNING!")
    print(f"• Interactive Dashboard: file://{dashboard_html}")
    print("• FastAPI Backend API:   http://127.0.0.1:8000")
    print("• Interactive API Docs:  http://127.0.0.1:8000/docs")
    print("• Telemetry Endpoint:    http://127.0.0.1:8000/api/v1/ingest/telemetry")
    print("=" * 65)
    print("Press Ctrl+C to shut down backend and exit.")

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down Zerthiva backend...")
        backend_proc.terminate()
        backend_proc.wait()
        print("Backend stopped cleanly. Good luck with your presentation!")

if __name__ == "__main__":
    main()
