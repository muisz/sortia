from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.enums import RoleEnum
from apps.utils import messages
from apps.utils.models import BaseModel
from apps.utils.generators import generate_otp


class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    picture = models.ImageField(upload_to='users/', null=True, blank=True)

    role = models.CharField(max_length=1, choices=((enum.value, enum.name) for enum in RoleEnum))

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'.strip()
    
    @classmethod
    def register_buyer(cls, name: str, username: str, email: str, password: str):
        return cls.register(name, username, email, password, RoleEnum.Buyer)
    
    @classmethod
    def register_seller(cls, name: str, username: str, email: str, password: str):
        return cls.register(name, username, email, password, RoleEnum.Seller)
    
    @classmethod
    def register(cls, name: str, username: str, email: str, password: str, role: RoleEnum):
        user = cls(
            username=username,
            role=role.value,
            is_active=False,
        )
        user.set_name(name)
        user.set_email(email)
        user.set_password(password)
        user.save()

        # send OTP
        OTPCode.create_otp_from(user.email)

        return user
    
    @classmethod
    def authenticate(cls, email: str, password: str):
        user = cls.objects.filter(email=email.lower()).first()
        if user is None:
            raise NotFound(messages.USER_EMAIL_NOT_FOUND)
        if not user.check_password(password):
            raise NotFound(messages.USER_INVALID_PASSWORD)
        if not user.is_active:
            raise NotFound(messages.USER_REQUIRE_ACTIVATION)
        return user
    
    @classmethod
    def get_from_email(cls, value: str, raise_exception: bool = False):
        user = cls.objects.filter(email=value.lower()).first()
        if not user and raise_exception:
            raise NotFound(messages.USER_EMAIL_NOT_FOUND)
        return user

    def set_name(self, value: str):
        names = value.split(' ')
        first_name = names[0]
        last_name = ''
        if len(names) > 1:
            last_name = ''.join(name for name in names[1:])
        self.first_name = first_name
        self.last_name = last_name

    def set_email(self, value: str):
        self.email = value.lower()

    def set_auth_token(self):
        token = RefreshToken.for_user(self)
        auth = {"access": str(token.access_token), "refresh": str(token)}
        self.token = auth
    
    def update_last_login(self):
        self.last_login = timezone.now()
        self.save()
    
    def activate(self):
        self.is_active = True
        self.save()


class OTPCode(BaseModel):
    code = models.CharField(max_length=6, primary_key=True)
    identifier = models.CharField(max_length=100)
    expired_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def create_otp_from(cls, identifier):
        otp = cls.objects.create(
            code=generate_otp(6),
            identifier=identifier,
            expired_at=timezone.now() + timedelta(minutes=5)
        )
        otp.invalidate_previous_otps()
        return otp

    @classmethod
    def claim(cls, code, from_identifier):
        otp = cls.verify(code, from_identifier)
        otp.used_at = timezone.now()
        otp.is_active = False
        otp.save()
    
    @classmethod
    def verify(cls, code, from_identifier):
        otp = cls.objects.filter(code=code, identifier=from_identifier).first()
        if otp is None:
            raise NotFound(messages.USER_OTP_NOT_FOUND)
        if otp.is_expired():
            raise NotFound(messages.USER_OTP_EXPIRED)
        if otp.used_at is not None:
            raise NotFound(messages.USER_OTP_ALREADY_USED)
        return otp

    def is_expired(self):
        now = timezone.now()
        return now > self.expired_at

    def invalidate_previous_otps(self):
        previous_otps = OTPCode.objects.filter(identifier=self.identifier, used_at__isnull=True).exclude(code=self.code)
        for otp in previous_otps:
            otp.make_expired()
    
    def make_expired(self):
        self.expired_at = self.created_at
        self.save()
