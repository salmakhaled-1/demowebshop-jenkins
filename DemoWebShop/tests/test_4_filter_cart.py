import re
from playwright.sync_api import expect
from Pages.product_page import ProductPage
from Pages.cart_page import CartPage



def test_books_checkout_flow(logged_in_page):
    page = logged_in_page

    product = ProductPage(page)
    product.open_books()
    product.filter_under_25()
    product.assert_all_prices_under_25()

    product_name = product.get_first_product_name()
    product.add_first_product_to_cart()

    cart = CartPage(page)
    cart.open_cart()
    cart.assert_product_in_cart(product_name)
    cart.accept_terms_and_checkout()

    