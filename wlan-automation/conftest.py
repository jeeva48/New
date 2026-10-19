"""Shared fixtures: config, mock router, Playwright browser, logged-in RouterPage."""
import pytest

from utils.config import load_config


@pytest.fixture(scope="session")
def cfg():
    return load_config()


@pytest.fixture(scope="session")
def is_mock(cfg):
    return cfg["mode"] == "mock"


@pytest.fixture(scope="session", autouse=True)
def mock_router(cfg):
    """Start the fake router only in mock mode."""
    if cfg["mode"] != "mock":
        yield None
        return
    from mock_router.server import start_server
    port = int(cfg["router"]["url"].rsplit(":", 1)[-1])
    server = start_server(port)
    yield server
    server.shutdown()


@pytest.fixture(scope="session")
def browser():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


@pytest.fixture
def page(browser):
    context = browser.new_context()
    pg = context.new_page()
    yield pg
    context.close()


@pytest.fixture
def router(page, cfg):
    """A RouterPage that is already logged in and on the wireless settings page."""
    from pages.router_page import RouterPage
    r = RouterPage(page, cfg["router"]["url"])
    r.open().login(cfg["router"]["username"], cfg["router"]["password"])
    r.go_to_wireless()
    return r


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save a screenshot when a GUI test fails (shows up next to the report)."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed and "page" in item.funcargs:
        item.funcargs["page"].screenshot(path=f"reports/{item.name}.png")
