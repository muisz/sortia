from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from faker import Faker
from rest_framework.exceptions import NotFound, ValidationError

from apps.users.models import OTPCode
from apps.utils import messages
from apps.utils.decoratos import assert_raise_error
from apps.utils.generators import generate_otp

fake = Faker()


class OTPCodeTestCase(TestCase):
    def test_create_otp_from_method(self):
        email = fake.email()
        otp = OTPCode.create_otp_from(email)

        self.assertIsNotNone(otp.code)

    def test_claim_method(self):
        email = fake.email()
        otp = OTPCode.create_otp_from(email)
        otp.claim(otp.code, email)
        otp.refresh_from_db()

        self.assertIsNotNone(otp.used_at)

    def test_verify_method(self):
        email = fake.email()
        otp = OTPCode.create_otp_from(email)
        otp_from_method = OTPCode.verify(otp.code, email)

        self.assertEqual(otp_from_method, otp)

    @assert_raise_error(NotFound(messages.USER_OTP_NOT_FOUND))
    def test_verify_method_raise_not_found(self):
        OTPCode.verify('00', fake.email())

    @assert_raise_error(NotFound(messages.USER_OTP_EXPIRED))
    def test_verify_method_raise_expired(self):
        email = fake.email()
        otp = OTPCode.create_otp_from(email)
        otp.expired_at = otp.expired_at + timedelta(minutes=-5)
        otp.save()

        OTPCode.verify(otp.code, email)
        
    @assert_raise_error(NotFound(messages.USER_OTP_ALREADY_USED))
    def test_verify_method_raise_expired(self):
        email = fake.email()
        otp = OTPCode.create_otp_from(email)
        otp.used_at = timezone.now()
        otp.save()

        OTPCode.verify(otp.code, email)

    def test_is_expired_method(self):
        otp = OTPCode.create_otp_from(fake.email())

        self.assertFalse(otp.is_expired())

    def test_invalidate_previous_otps(self):
        email = fake.email()
        previous_otps = [
            OTPCode.objects.create(
                code=generate_otp(6),
                identifier=email,
                expired_at=timezone.now() + timedelta(minutes=5)
            ) for i in range(3)
        ]
        new_otp = OTPCode.objects.create(
            code=generate_otp(6),
            identifier=email,
            expired_at=timezone.now() + timedelta(minutes=5)
        )
        new_otp.invalidate_previous_otps()

        for previous_otp in previous_otps:
            previous_otp.refresh_from_db()
            self.assertTrue(previous_otp.is_expired())
        self.assertFalse(new_otp.is_expired())

    def test_make_expired_method(self):
        otp = OTPCode.create_otp_from(fake.email())
        otp.make_expired()

        self.assertTrue(otp.is_expired())