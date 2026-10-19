"""A tiny fake router admin GUI so the Playwright tests run without hardware.

Pages: /login (admin / admin123), /wireless (SSID, security, channel).
Run manually:  python -m mock_router.server   ->  http://127.0.0.1:8080
"""
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

STATE = {
    "ssid": "DefaultWiFi",
    "security": "WPA2",
    "channel": "6",
    "logged_in": False,
}
USER, PASSWORD = "admin", "admin123"

LOGIN_HTML = """<!doctype html><html><body><h1>Router Login</h1>
<form method="post" action="/login">
  <input id="user" name="user" placeholder="Username">
  <input id="pass" name="pass" type="password" placeholder="Password">
  <button type="submit">Login</button>
</form><p id="msg" style="color:red">{msg}</p></body></html>"""

WIRELESS_HTML = """<!doctype html><html><body><h1>Wireless Settings</h1>
<form method="post" action="/wireless">
  <label>SSID <input id="ssid" name="ssid" value="{ssid}"></label>
  <label>Security
    <select id="security" name="security">
      <option {o_wpa2}>WPA2</option><option {o_wpa3}>WPA3</option>
    </select></label>
  <label>Channel
    <select id="channel" name="channel">
      <option {c1}>1</option><option {c6}>6</option><option {c11}>11</option>
    </select></label>
  <button type="submit">Save</button>
</form><p id="status">{status}</p></body></html>"""


def _render_wireless(status=""):
    sel = "selected"
    return WIRELESS_HTML.format(
        ssid=STATE["ssid"], status=status,
        o_wpa2=sel if STATE["security"] == "WPA2" else "",
        o_wpa3=sel if STATE["security"] == "WPA3" else "",
        c1=sel if STATE["channel"] == "1" else "",
        c6=sel if STATE["channel"] == "6" else "",
        c11=sel if STATE["channel"] == "11" else "",
    )


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep test output clean
        pass

    def _send(self, body, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode())

    def _redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def _form(self):
        length = int(self.headers.get("Content-Length", 0))
        data = parse_qs(self.rfile.read(length).decode())
        return {k: v[0] for k, v in data.items()}

    def do_GET(self):
        if self.path == "/wireless":
            if not STATE["logged_in"]:
                return self._redirect("/login")
            return self._send(_render_wireless())
        return self._send(LOGIN_HTML.format(msg=""))

    def do_POST(self):
        form = self._form()
        if self.path == "/login":
            if form.get("user") == USER and form.get("pass") == PASSWORD:
                STATE["logged_in"] = True
                return self._redirect("/wireless")
            return self._send(LOGIN_HTML.format(msg="Invalid credentials"))
        if self.path == "/wireless" and STATE["logged_in"]:
            ssid = form.get("ssid", "").strip()
            if not ssid or len(ssid) > 32:
                return self._send(_render_wireless("Error: SSID must be 1-32 characters"))
            STATE.update(ssid=ssid, security=form.get("security", "WPA2"),
                         channel=form.get("channel", "6"))
            return self._send(_render_wireless("Saved successfully"))
        return self._redirect("/login")


def start_server(port: int = 8080):
    """Start in a background thread; returns the server (call .shutdown() to stop)."""
    STATE.update(ssid="DefaultWiFi", security="WPA2", channel="6", logged_in=False)
    server = HTTPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


if __name__ == "__main__":
    print("Mock router on http://127.0.0.1:8080  (admin / admin123)")
    HTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
