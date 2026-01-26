from Pages.login_page import LoginPage


def test_login_success(page):
    login = LoginPage(page)
    login.open_login()
    login.login("salmak12345@gmail.com", "s@lma12345")
    login.assert_login_success()


def test_login_wrong_password(page):
    login = LoginPage(page)
    login.open_login()
    login.login("salmak12345@gmail.com", "WRONG_PASSWORD")
    login.assert_login_error()
    
