from Pages.account_page import AccountPage



def test_account_info_add_address(logged_in_page):

    account = AccountPage(logged_in_page)
    account.open_addresses()
    account.add_new_address(
        first_name="mariam",
        last_name="jana",
        email="janakk12345@gmail.com",
        country="Belgium",
        city="cairo",
        address="10 street",
        zip_code="203456",
        phone="0123456789",
        fax="12345"
    )
