"""Playwright tests for the router's Wireless Settings page."""
import pytest

pytestmark = pytest.mark.gui


def test_login_success(page, cfg):
    from pages.router_page import RouterPage
    r = RouterPage(page, cfg["router"]["url"]).open()
    r.login(cfg["router"]["username"], cfg["router"]["password"])
    page.wait_for_url("**/wireless")
    assert page.locator("h1").inner_text() == "Wireless Settings"


def test_login_wrong_password(page, cfg):
    from pages.router_page import RouterPage
    r = RouterPage(page, cfg["router"]["url"]).open()
    r.login(cfg["router"]["username"], "wrong-password")
    assert page.locator("#msg").inner_text() == "Invalid credentials"


def test_change_ssid_and_persist(router):
    router.configure(ssid="TestWiFi_Automation")
    assert router.status_text.inner_text() == "Saved successfully"
    router.go_to_wireless()                      # reload: proves it was really saved
    assert router.current_ssid() == "TestWiFi_Automation"


@pytest.mark.parametrize("channel", [1, 6, 11])
def test_change_channel(router, channel):
    router.configure(channel=channel)
    assert router.status_text.inner_text() == "Saved successfully"
    router.go_to_wireless()
    assert router.current_channel() == str(channel)


def test_enable_wpa3(router):
    router.configure(security="WPA3")
    router.go_to_wireless()
    assert router.current_security() == "WPA3"


def test_empty_ssid_rejected(router):
    router.configure(ssid="")
    assert "Error" in router.status_text.inner_text()


def test_ssid_too_long_rejected(router):
    router.configure(ssid="X" * 33)              # max SSID length is 32 bytes
    assert "Error" in router.status_text.inner_text()
