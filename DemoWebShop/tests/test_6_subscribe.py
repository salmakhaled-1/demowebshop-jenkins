from Pages.home_page import HomePage

def test_subscribe_after_login(logged_in_page):
    home = HomePage(logged_in_page)

    home.subscribe_to_newsletter("salma12@gmail.com")
    home.assert_subscribe_success()
