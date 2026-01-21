import pytest
from playwright.sync_api import sync_playwright
from Pages.login_page import LoginPage

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
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
    page.close()

@pytest.fixture
def logged_in_page(page):
    login = LoginPage(page)
    login.open_login()
    login.login("salmak12345@gmail.com", "s@lma12345")
    login.assert_login_success()
    return page



import os
import pytest
import allure

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Run all other hooks to get the report object.
    outcome = yield
    rep = outcome.get_result()

    # Only on test failures in the call phase (not setup/teardown)
    if rep.when == "call" and rep.failed:
        # Try to access Playwright page fixture if available
        page = item.funcargs.get("page") or item.funcargs.get("logged_in_page")
        if page:
            try:
                # Ensure artifacts dir exists
                os.makedirs("artifacts/playwright", exist_ok=True)
                screenshot_path = os.path.join("artifacts", "playwright", f"{item.name}.png")
                page.screenshot(path=screenshot_path, full_page=True)
                with open(screenshot_path, "rb") as f:
                    allure.attach(f.read(), name=f"{item.name}_screenshot", attachment_type=allure.attachment_type.PNG)
            except Exception as e:
                # Avoid breaking the test outcome because of attachment issues
                print(f"[WARN] Could not capture/attach screenshot: {e}")


