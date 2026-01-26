from Pages.login_page import LoginPage
from Pages.home_page import HomePage

def test_community_poll(logged_in_page):
    page = logged_in_page

    home = HomePage(page)
    home.vote_in_community_poll(option_id=2)
    home.assert_poll_voted()

