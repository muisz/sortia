from django.test import TestCase
from faker import Faker
from rest_framework.exceptions import NotFound

from apps.users.enums import RoleEnum
from apps.users.models import User
from apps.utils import messages
from apps.utils.decoratos import assert_raise_error

fake = Faker()


class UserTestCase(TestCase):
    def test_register_method(self):
        user = User.register(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
            role=RoleEnum.Buyer,
        )

        self.assertIsNotNone(user.id)

    def test_register_buyer_method(self):
        user = User.register_buyer(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )

        self.assertIsNotNone(user.id)
        self.assertEqual(user.role, RoleEnum.Buyer.value)

    def test_register_seller_method(self):
        user = User.register_seller(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )

        self.assertIsNotNone(user.id)
        self.assertEqual(user.role, RoleEnum.Seller.value)
    
    def test_authenticate_method(self):
        password = fake.password()
        user = User.register_seller(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.email(),
            password=password,
        )
        user.activate()

        user_from_method = User.authenticate(user.email, password)
        self.assertEqual(user_from_method, user)
    
    @assert_raise_error(NotFound(messages.USER_EMAIL_NOT_FOUND))
    def test_authenticate_method_raise_not_found(self):
        User.authenticate(fake.email(), fake.password())
    
    @assert_raise_error(NotFound(messages.USER_INVALID_PASSWORD))
    def test_authenticate_method_raise_invalid_password(self):
        user = User.register_seller(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )
        User.authenticate(user.email, fake.password())
    
    @assert_raise_error(NotFound(messages.USER_REQUIRE_ACTIVATION))
    def test_authenticate_method_raise_user_not_active(self):
        password = fake.password()
        user = User.register_seller(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.email(),
            password=password,
        )
        User.authenticate(user.email, password)
    
    def test_get_from_email_method(self):
        user = User.register_seller(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )
        user_from_method = User.get_from_email(user.email)

        self.assertEqual(user, user_from_method)
    
    def test_get_from_email_method_return_none(self):
        result = User.get_from_email(fake.email())

        self.assertIsNone(result)
    
    @assert_raise_error(NotFound(messages.USER_EMAIL_NOT_FOUND))
    def test_get_from_email_raise_not_found(self):
        User.get_from_email(fake.email(), raise_exception=True)

    def test_set_name_method(self):
        first_name = fake.first_name()
        last_name = fake.last_name()
        user = User()
        user.set_name(first_name + ' ' + last_name)

        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
    
    def test_name_property(self):
        first_name = fake.first_name()
        last_name = fake.last_name()
        name = first_name + ' ' + last_name
        user = User()
        user.set_name(name)

        self.assertEqual(user.name, name)
    
    def test_set_email_property(self):
        email = fake.email()
        user = User()
        user.set_email(email.upper())

        self.assertEqual(user.email, email.lower())

    def test_set_auth_token_method(self):
        user = User.register_buyer(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )
        user.set_auth_token()

        self.assertTrue(hasattr(user, 'token'))
        self.assertIsNotNone(user.token)
    
    def test_update_last_login_method(self):
        user = User.register_buyer(
            name=fake.name(),
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )
        user.update_last_login()

        self.assertIsNotNone(user.last_login)
