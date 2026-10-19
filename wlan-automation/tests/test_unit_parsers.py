"""Pure-Python tests: no browser, router or Wi-Fi hardware required."""
import pytest

from utils.iperf_runner import SAMPLE_IPERF_JSON, parse_iperf3
from utils.roaming import SAMPLE_ROAM_LOG, analyse_roam
from utils.wifi_metrics import (SAMPLE_IW_LINK, band_from_freq, parse_iw_link,
                                rssi_quality)

pytestmark = pytest.mark.unit


def test_parse_iw_link_fields():
    info = parse_iw_link(SAMPLE_IW_LINK)
    assert info["connected"] is True
    assert info["ssid"] == "TestWiFi"
    assert info["bssid"] == "aa:bb:cc:dd:ee:01"
    assert info["rssi_dbm"] == -58
    assert info["band"] == "5GHz"
    assert info["rx_mbps"] == 866.7


def test_parse_iw_link_not_connected():
    assert parse_iw_link("Not connected.") == {"connected": False}


@pytest.mark.parametrize("freq,band", [
    (2412, "2.4GHz"), (2462, "2.4GHz"),
    (5180, "5GHz"), (5745, "5GHz"),
    (5955, "6GHz"), (None, None),
])
def test_band_from_freq(freq, band):
    assert band_from_freq(freq) == band


@pytest.mark.parametrize("rssi,quality", [
    (-45, "excellent"), (-60, "good"), (-72, "fair"), (-85, "poor"),
])
def test_rssi_quality(rssi, quality):
    assert rssi_quality(rssi) == quality


def test_parse_iperf3():
    result = parse_iperf3(SAMPLE_IPERF_JSON)
    assert result["throughput_mbps"] == 409.8
    assert result["retransmits"] == 3


def test_parse_iperf3_error_json():
    with pytest.raises(RuntimeError, match="unable to connect"):
        parse_iperf3('{"error": "unable to connect to server"}')


def test_analyse_roam_sample():
    result = analyse_roam(SAMPLE_ROAM_LOG)
    assert result["roam_count"] == 1
    assert result["bssid_sequence"] == ["aa:bb:cc:dd:ee:01", "aa:bb:cc:dd:ee:02"]
    assert result["max_gap_sec"] == pytest.approx(0.3)


def test_analyse_roam_no_roam():
    log = [(0.0, "aa:bb:cc:dd:ee:01"), (1.0, "aa:bb:cc:dd:ee:01")]
    assert analyse_roam(log)["roam_count"] == 0
