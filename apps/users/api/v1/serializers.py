from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.enums import RoleEnum
from apps.users.models import User as user_model

User: user_model = get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = User
        fields = ('name', 'username', 'email', 'password')


class RegisterBuyerSerializer(RegisterUserSerializer):
    pass


class RegisterSellerSerializer(RegisterUserSerializer):
    pass


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, obj: user_model):
        return RoleEnum.display_name(obj.role)

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'role', 'date_joined', 'last_login')


class AuthUserSerializer(UserSerializer):
    token = serializers.SerializerMethodField()

    def get_token(self, obj: user_model):
        return obj.token

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'email', 'role', 'date_joined', 'last_login', 'token')


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class SendOTPSerializer(serializers.Serializer):
    identifier = serializers.CharField()


class OTPSerializer(serializers.Serializer):
    code = serializers.CharField()
    identifier = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ForgotPasswordVerifySerializer(OTPSerializer):
    new_password = serializers.CharField()
