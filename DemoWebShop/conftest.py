import pytest
from playwright.sync_api import sync_playwright
from Pages.login_page import LoginPage


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
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
    page.goto("https://demowebshop.tricentis.com/")
    yield page
    page.close()


@pytest.fixture(scope="session", autouse=True)
def allure_env():
    os.makedirs("allure-results", exist_ok=True)
    with open("allure-results/environment.properties", "w", encoding="utf-8") as f:
        f.write(f"Headless={HEADLESS}\n")
        f.write(f"RecordVideo={RECORD_VIDEO}\n")
        f.write(f"Trace={TRACE}\n")
        f.write("Browser=Chromium\n")



@pytest.fixture
def logged_in_page(page):

    login = LoginPage(page)

    login.login_successful(
        "salmak12345@gmail.com",
        "s@lma12345"
    )

    yield page
