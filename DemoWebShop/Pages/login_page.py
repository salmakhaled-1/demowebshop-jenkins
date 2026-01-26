from playwright.sync_api import Page, expect


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    def open_login(self):
        self.page.get_by_role("link", name="Log in").click()
        expect(self.page.locator("#Email")).to_be_visible()

    def login(self, email: str, password: str):
        self.page.locator("#Email").fill(email)
        self.page.locator("#Password").fill(password)
        self.page.get_by_role("button", name="Log in").click()

    def assert_login_success(self):
        expect(self.page.get_by_role("link", name="My account")).to_be_visible()

    def assert_login_error(self):
        error_message = (
            "Login was unsuccessful. Please correct the errors and try again."
        )
        error = self.page.locator(".validation-summary-errors span")
        expect(error).to_be_visible()
        expect(error).to_have_text(error_message)

    # ✅ MUST be inside the class
    def login_successful(self, email: str, password: str):
        self.open_login()
        self.login(email, password)
        self.assert_login_success()