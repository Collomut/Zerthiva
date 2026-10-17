"""
SoilGuard Automated Field Telemetry Streamer
Sends synthetic time-series telemetry to the cloud backend or outputs to stdout.
"""

import sys
import time
import json
import argparse
import urllib.request
import urllib.error
from mock_field_node import MockFieldNode


def stream_telemetry(endpoint: str, psk: str, node_id: str, crop: str, interval: float, steps: int, standalone: bool):
    print("=" * 60)
    print("🌱 SoilGuard Synthetic Field Node Streamer")
    print(f"Device ID:  {node_id}")
    print(f"Crop Type:  {crop}")
    print(f"Mode:       {'Standalone JSON' if standalone else 'Live HTTP POST'}")
    if not standalone:
        print(f"Endpoint:   {endpoint}")
    print("=" * 60)

    node = MockFieldNode(device_id=node_id, crop=crop, base_ec=1.2)
    step_count = 0

    while True:
        data = node.step(hour_increment=1)
        step_count += 1

        if standalone:
            print(json.dumps(data))
        else:
            payload_bytes = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=payload_bytes,
                headers={
                    "Content-Type": "application/json",
                    "X-Device-PSK": psk
                },
                method="POST"
            )

            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    res_body = response.read().decode("utf-8")
                    res_json = json.loads(res_body)
                    print(f"[{time.strftime('%X')}] Day {data['day']:02d} {data['hour']:02d}:00 | Temp: {data['soil_temp_c']}°C | EC: {data['raw_ec']} dS/m | Moist: {data['moisture_vwc']}% -> Ingested ({res_json.get('status')}) Advisory: {res_json.get('advisory')}")
            except urllib.error.HTTPError as e:
                err_text = e.read().decode("utf-8")
                print(f"HTTP Error {e.code}: {err_text}", file=sys.stderr)
            except Exception as e:
                print(f"Connection failed: {e}", file=sys.stderr)

        if steps > 0 and step_count >= steps:
            print(f"\nSimulation finished after {step_count} cycles.")
            break

        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="SoilGuard Telemetry Simulator")
    parser.add_argument("--endpoint", default="http://localhost:8000/api/v1/ingest/telemetry", help="Backend ingest URL")
    parser.add_argument("--psk", default="sg-field-device-pre-shared-key-2026", help="Device Pre-Shared Key")
    parser.add_argument("--node-id", default="SG-NODE-001", help="Node ID")
    parser.add_argument("--crop", default="tomato", help="Crop profile")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval in seconds between telemetry cycles")
    parser.add_argument("--steps", type=int, default=0, help="Total cycles to run (0 for infinite)")
    parser.add_argument("--standalone", action="store_true", help="Print to console without sending HTTP requests")

    args = parser.parse_args()
    stream_telemetry(
        endpoint=args.endpoint,
        psk=args.psk,
        node_id=args.node_id,
        crop=args.crop,
        interval=args.interval,
        steps=args.steps,
        standalone=args.standalone
    )


if __name__ == "__main__":
    main()
