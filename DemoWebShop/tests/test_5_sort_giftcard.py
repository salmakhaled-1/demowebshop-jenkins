from playwright.sync_api import sync_playwright, expect
from Pages.login_page import LoginPage
from Pages.gift_cards_page import GiftCardsPage

def test_gift_card_flow(logged_in_page):
    

    page = logged_in_page
    gift = GiftCardsPage(page)
    gift.open_gift_cards()
    gift.sort_price_high_to_low()
    gift.assert_prices_sorted_high_to_low()
    gift.add_third_product_to_cart()
    gift.fill_gift_card_details()
    gift.email_a_friend()
