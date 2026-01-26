
# conftest.py (only the essentials for failure attachments)
import os
import pytest
import allure
from allure_commons.types import AttachmentType
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def playwright():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright):
    browser = playwright.chromium.launch(headless=True)  # headless ok for CI
    yield browser
    browser.close()

@pytest.fixture
def context(browser):
    context = browser.new_context()
    yield context
    context.close()

@pytest.fixture
def page(context):
    page = context.new_page()
    page.goto("https://demowebshop.tricentis.com/", wait_until="domcontentloaded")
    yield page
    try:
        page.close()
    except Exception:
        pass

# ---- Hook that captures artifacts on failure ----
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or not report.failed:
        return

    page = item.funcargs.get("page", None)
    if not page:
        return

    safe_name = (
        item.nodeid.replace("::", " - ")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
        .replace(" ", "_")
    )

    # Screenshot
    try:
        png = page.screenshot(full_page=False)
        allure.attach(png, name=f"Screenshot - {safe_name}", attachment_type=AttachmentType.PNG)
    except Exception:
        pass

    # DOM HTML
    try:
        html = page.content()
        allure.attach(html, name=f"DOM - {safe_name}", attachment_type=AttachmentType.HTML)
    except Exception:
        pass

    # Current URL
    try:
        allure.attach(page.url, name="Current URL", attachment_type=AttachmentType.TEXT)
    except Exception:
        pass
