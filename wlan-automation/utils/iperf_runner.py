"""Run iperf3 and parse its JSON output."""
import json
import subprocess

# Trimmed real-format iperf3 -J output used in mock mode and unit tests.
SAMPLE_IPERF_JSON = json.dumps({
    "end": {
        "sum_sent": {"bits_per_second": 412_500_000.0, "retransmits": 3},
        "sum_received": {"bits_per_second": 409_800_000.0},
    }
})


def run_iperf3(server: str, duration: int = 10, reverse: bool = False) -> str:
    cmd = ["iperf3", "-c", server, "-t", str(duration), "-J"]
    if reverse:
        cmd.append("-R")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30)
    if result.returncode != 0:
        raise RuntimeError(f"iperf3 failed: {result.stderr or result.stdout}")
    return result.stdout


def parse_iperf3(raw_json: str) -> dict:
    data = json.loads(raw_json)
    if "error" in data:
        raise RuntimeError(f"iperf3 error: {data['error']}")
    end = data["end"]
    return {
        "throughput_mbps": round(end["sum_received"]["bits_per_second"] / 1e6, 2),
        "retransmits": end["sum_sent"].get("retransmits", 0),
    }
