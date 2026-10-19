"""Parse Wi-Fi link info from `iw dev <if> link` output."""
import re

SAMPLE_IW_LINK = """\
Connected to aa:bb:cc:dd:ee:01 (on wlan0)
\tSSID: TestWiFi
\tfreq: 5180
\tRX: 123456 bytes (900 packets)
\tTX: 65432 bytes (500 packets)
\tsignal: -58 dBm
\trx bitrate: 866.7 MBit/s VHT-MCS 9 80MHz short GI VHT-NSS 2
\ttx bitrate: 780.0 MBit/s VHT-MCS 8 80MHz short GI VHT-NSS 2
"""


def parse_iw_link(text: str) -> dict:
    """Return dict with connected, bssid, ssid, freq_mhz, band, rssi_dbm, rx/tx bitrate."""
    if "Not connected" in text or not text.strip():
        return {"connected": False}

    def grab(pattern, cast=str):
        m = re.search(pattern, text)
        return cast(m.group(1)) if m else None

    freq = grab(r"freq:\s*(\d+)", int)
    return {
        "connected": True,
        "bssid": grab(r"Connected to ([0-9a-fA-F:]{17})"),
        "ssid": grab(r"SSID:\s*(.+)"),
        "freq_mhz": freq,
        "band": band_from_freq(freq),
        "rssi_dbm": grab(r"signal:\s*(-?\d+)", int),
        "rx_mbps": grab(r"rx bitrate:\s*([\d.]+)", float),
        "tx_mbps": grab(r"tx bitrate:\s*([\d.]+)", float),
    }


def band_from_freq(freq_mhz):
    if freq_mhz is None:
        return None
    if 2400 <= freq_mhz < 2500:
        return "2.4GHz"
    if 5000 <= freq_mhz < 5900:
        return "5GHz"
    if 5925 <= freq_mhz <= 7125:
        return "6GHz"
    return "unknown"


def rssi_quality(rssi_dbm: int) -> str:
    if rssi_dbm >= -50:
        return "excellent"
    if rssi_dbm >= -65:
        return "good"
    if rssi_dbm >= -75:
        return "fair"
    return "poor"
