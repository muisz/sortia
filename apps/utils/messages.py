from django.utils.translation import gettext_lazy as _


USER_EMAIL_NOT_FOUND = _("email not found.")
USER_INVALID_PASSWORD = _("invalid password.")
USER_REQUIRE_ACTIVATION = _("user not activated yet. Please activate your account.")
USER_ACCOUNT_CREATED = _("account created. We have sent otp to your email to verify your account.")

USER_OTP_NOT_FOUND = _("otp not found.")
USER_OTP_EXPIRED = _("otp expired. Please request the new otp.")
USER_OTP_ALREADY_USED = _("otp already used. Please request the new otp.")
USER_OTP_SENT = _("otp sent!")