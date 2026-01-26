from Pages.logout_page import LogoutPage


def test_user_can_logout(logged_in_page):

    logout = LogoutPage(logged_in_page)

    logout.logout()
    logout.assert_logout_success()