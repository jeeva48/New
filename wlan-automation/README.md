# WLAN Test Automation Framework (Python + Playwright + pytest)

Portfolio project for WLAN / network automation roles. It automates:

1. **Router/AP web GUI** with Playwright (Page Object Model)
2. **WLAN link checks**: RSSI, band, bitrate parsed from `iw dev wlan0 link`
3. **Throughput tests** with `iperf3` (JSON parsed, pass/fail vs a threshold)
4. **Roaming analysis**: BSSID changes and connectivity gap during handover
5. **SSH access** to APs/clients with paramiko
6. **HTML report** with pytest-html, plus failure screenshots

## Quick start (no hardware needed: mock mode)

```bash
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
pytest
```

Open `reports/report.html` for the result. In mock mode a fake router GUI is started
automatically and canned `iw`/`iperf3` output is used.

Run subsets:

```bash
pytest -m unit          # parsers only, no browser
pytest -m gui           # Playwright GUI tests
pytest -m wlan          # signal / throughput / roaming
pytest -k ssid -s       # by name, show prints
```

## Using it with real hardware

Edit `config/config.yaml`:

- `mode: real`
- `router.url`, username, password -> your AP
- `wlan.interface`, `wlan.iperf_server` -> your Linux test client and an iperf3 server (`iperf3 -s`)
- Adjust locators in `pages/router_page.py` to match your AP's HTML (use `playwright codegen <url>` to find them)

## Structure

```
config/config.yaml        thresholds, credentials, mode switch
conftest.py               fixtures: config, mock router, browser, logged-in page
pages/router_page.py      Page Object for the router GUI
mock_router/server.py     fake router admin site for demo/CI
utils/wifi_metrics.py     iw link parser, band/RSSI helpers
utils/iperf_runner.py     run + parse iperf3
utils/roaming.py          roam count and gap analysis
utils/ssh_client.py       paramiko wrapper
tests/                    unit, GUI and WLAN tests
```

## Interview talking points

- **Why Page Object Model?** Locators live in one file; when the AP firmware changes its HTML, one file changes, not 50 tests.
- **Why Playwright over Selenium?** Auto-waiting (fewer flaky tests), faster, built-in tracing/screenshots, easy codegen.
- **Why a mock mode?** Tests and parsers run in CI without hardware; the same tests switch to real devices with one config flag.
- **Why parametrize?** One test body covers channels 1/6/11, WPA2/WPA3: more coverage, less code.
- **How do you handle flaky Wi-Fi results?** Repeat runs, use averages/percentiles, and set thresholds with margin.
- **Roaming test in real life:** walk a client between two APs, sample `iw dev wlan0 link` every 100 ms, feed the log to `analyse_roam()`, assert gap < limit (e.g. 50 ms for 802.11r).

## Ideas to extend (makes the project stronger)

- Add `scapy`/`tshark` capture to verify 802.11 association frames
- Add WPA3/SAE negotiation checks
- Run in GitHub Actions in mock mode
- Add a multi-client load test with several iperf3 streams
