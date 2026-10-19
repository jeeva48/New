"""Analyse a roaming log: a list of (timestamp_sec, bssid_or_None) samples.

bssid is None when the client had no link (the roam gap).
Real use: poll `iw dev wlan0 link` once per 100 ms while walking between APs.
"""


def analyse_roam(samples):
    """Return roam count, BSSID sequence and the longest no-connectivity gap."""
    bssids, roams, max_gap = [], 0, 0.0
    gap_start = None
    last_bssid = None

    for ts, bssid in samples:
        if bssid is None:
            if gap_start is None:
                gap_start = ts
            continue
        if gap_start is not None:
            max_gap = max(max_gap, ts - gap_start)
            gap_start = None
        if bssid != last_bssid:
            if last_bssid is not None:
                roams += 1
            bssids.append(bssid)
            last_bssid = bssid

    return {"roam_count": roams, "bssid_sequence": bssids, "max_gap_sec": round(max_gap, 3)}


# Simulated walk from AP1 to AP2 with a 0.3 s handover gap.
SAMPLE_ROAM_LOG = [
    (0.0, "aa:bb:cc:dd:ee:01"), (0.5, "aa:bb:cc:dd:ee:01"),
    (1.0, "aa:bb:cc:dd:ee:01"), (1.5, None), (1.8, "aa:bb:cc:dd:ee:02"),
    (2.3, "aa:bb:cc:dd:ee:02"), (2.8, "aa:bb:cc:dd:ee:02"),
]
