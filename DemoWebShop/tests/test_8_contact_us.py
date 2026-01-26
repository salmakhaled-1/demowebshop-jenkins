from Pages.contact_us import ContactUsPage


def test_contact_us(logged_in_page):

    contact = ContactUsPage(logged_in_page)

    contact.open()
    contact.submit_enquiry(
        name="janaa salma",
        email="jana@gmail.com",
        enquiry="The shipping is late"
    )
    contact.assert_success_message()

