"""Page Object for the router web GUI.

Tests call high-level methods (login, set_ssid ...) and never touch locators directly.
If the real AP's HTML differs, only the locators in this file need to change.
"""
from playwright.sync_api import Page


class RouterPage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url.rstrip("/")

    # --- locators (change these for your real AP) ---
    @property
    def user_input(self):
        return self.page.locator("#user")

    @property
    def pass_input(self):
        return self.page.locator("#pass")

    @property
    def ssid_input(self):
        return self.page.locator("#ssid")

    @property
    def security_select(self):
        return self.page.locator("#security")

    @property
    def channel_select(self):
        return self.page.locator("#channel")

    @property
    def status_text(self):
        return self.page.locator("#status")

    # --- actions ---
    def open(self):
        self.page.goto(f"{self.base_url}/login")
        return self

    def login(self, username: str, password: str):
        self.user_input.fill(username)
        self.pass_input.fill(password)
        self.page.get_by_role("button", name="Login").click()
        return self

    def go_to_wireless(self):
        self.page.goto(f"{self.base_url}/wireless")
        return self

    def configure(self, ssid=None, security=None, channel=None):
        if ssid is not None:
            self.ssid_input.fill(ssid)
        if security is not None:
            self.security_select.select_option(security)
        if channel is not None:
            self.channel_select.select_option(str(channel))
        self.page.get_by_role("button", name="Save").click()
        return self

    # --- reads ---
    def current_ssid(self) -> str:
        return self.ssid_input.input_value()

    def current_channel(self) -> str:
        return self.channel_select.input_value()

    def current_security(self) -> str:
        return self.security_select.input_value()
