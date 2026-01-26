from playwright.sync_api import Page, expect


class LogoutPage:
    def __init__(self, page: Page):
        self.page = page

    def logout(self):
        # Click Logout link
        self.page.get_by_role("link", name="Log out").click()

    def assert_logout_success(self):
        # After logout, Login link should appear again
        expect(self.page.get_by_role("link", name="Log in")).to_be_visible()