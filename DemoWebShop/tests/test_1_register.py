from Pages.register_page import RegisterPage
from utils.data_generator import (
    generate_email,
    generate_password,
    generate_name
)

def test_register_new_user(page):
    register = RegisterPage(page)

    register.open()
    register.register(
        first_name=generate_name(),
        last_name=generate_name(),
        email=generate_email(),
        password=generate_password()
    )

    register.assert_registration_success()


def test_register_password_mismatch(page):
    register = RegisterPage(page)

    register.open()
    register.register(
        first_name=generate_name(),
        last_name=generate_name(),
        email=generate_email(),
        password="Password123!",
        confirm_password="DifferentPassword123!"
    )

    register.assert_password_mismatch_error()