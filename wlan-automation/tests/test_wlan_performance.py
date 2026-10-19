"""WLAN signal, throughput and roaming tests.

mock mode: uses canned iw / iperf3 / roam data so the logic is verifiable anywhere.
real mode: runs the real commands on your test client (Linux with iw + iperf3).
"""
import subprocess

import pytest

from utils.iperf_runner import (SAMPLE_IPERF_JSON, parse_iperf3, run_iperf3)
from utils.roaming import SAMPLE_ROAM_LOG, analyse_roam
from utils.wifi_metrics import SAMPLE_IW_LINK, parse_iw_link

pytestmark = pytest.mark.wlan


@pytest.fixture
def link_info(cfg, is_mock):
    if is_mock:
        return parse_iw_link(SAMPLE_IW_LINK)
    out = subprocess.run(
        ["iw", "dev", cfg["wlan"]["interface"], "link"],
        capture_output=True, text=True, check=True,
    ).stdout
    return parse_iw_link(out)


def test_client_is_connected(link_info):
    assert link_info["connected"], "Client is not associated to any AP"


def test_rssi_above_threshold(link_info, cfg):
    assert link_info["rssi_dbm"] >= cfg["thresholds"]["min_rssi_dbm"], (
        f"RSSI {link_info['rssi_dbm']} dBm is below the "
        f"{cfg['thresholds']['min_rssi_dbm']} dBm limit"
    )


def test_throughput_meets_minimum(cfg, is_mock):
    raw = SAMPLE_IPERF_JSON if is_mock else run_iperf3(
        cfg["wlan"]["iperf_server"], cfg["wlan"]["iperf_duration_sec"]
    )
    result = parse_iperf3(raw)
    minimum = cfg["thresholds"]["min_throughput_mbps"]
    assert result["throughput_mbps"] >= minimum, (
        f"Throughput {result['throughput_mbps']} Mbps < required {minimum} Mbps"
    )


def test_roaming_gap_within_limit(cfg, is_mock):
    if not is_mock:
        pytest.skip("Real roaming needs a walk-test log; feed it to analyse_roam()")
    result = analyse_roam(SAMPLE_ROAM_LOG)
    assert result["roam_count"] >= 1, "Client never roamed"
    assert result["max_gap_sec"] <= cfg["thresholds"]["max_roam_gap_sec"]
