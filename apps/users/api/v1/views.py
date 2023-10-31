from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.users.models import OTPCode, User as user_model
from apps.users.api.v1.serializers import (
    AuthUserSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ForgotPasswordVerifySerializer,
    LoginSerializer,
    OTPSerializer,
    RegisterBuyerSerializer,
    RegisterSellerSerializer,
    SendOTPSerializer,
    UserSerializer,
)
from apps.utils import messages

User: user_model = get_user_model()


class RegisterUserView(GenericViewSet):
    permission_classes = ()
    serializer_class = AuthUserSerializer

    @action(
        methods=['post'],
        detail=False,
        serializer_class=RegisterBuyerSerializer,
        permission_classes=(),
    )
    def buyer(self, request):
        serializer = self.serializer_class(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        User.register_buyer(
            name=validated_data['name'],
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        return Response({'message': messages.USER_ACCOUNT_CREATED}, status=status.HTTP_201_CREATED)
    
    @action(
        methods=['post'],
        detail=False,
        serializer_class=RegisterSellerSerializer,
        permission_classes=(),
    )
    def seller(self, request):
        serializer = self.serializer_class(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        User.register_seller(
            name=validated_data['name'],
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        return Response({'message': messages.USER_ACCOUNT_CREATED}, status=status.HTTP_201_CREATED)


class UserView(GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    @action(
        methods=['post'],
        detail=False,
        serializer_class=LoginSerializer,
        permission_classes=(),
    )
    def login(self, request):
        serializer = self.serializer_class(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = User.authenticate(validated_data['email'], validated_data['password'])
        user.set_auth_token()
        user.update_last_login()

        response_serializer = AuthUserSerializer(user, context=self.get_serializer_context())
        return Response(response_serializer.data)
    
    @action(
        methods=['post'],
        detail=False,
        serializer_class=OTPSerializer,
        permission_classes=(),
    )
    def activate(self, request):
        serializer = self.serializer_class(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        OTPCode.claim(validated_data['code'], validated_data['identifier'])
        user = User.get_from_email(validated_data['identifier'], raise_exception=True)
        user.activate()
        user.set_auth_token()
        user.update_last_login()

        response_serializer = AuthUserSerializer(user, context=self.get_serializer_context())
        return Response(response_serializer.data)

    @action(
        methods=['post'],
        detail=False,
        serializer_class=ChangePasswordSerializer,
        url_path='change-password',
    )
    def change_password(self, request):
        serializer = self.serializer_class(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user: user_model = request.user
        user.change_password(validated_data['old_password'], validated_data['new_password'])

        return Response({'message': messages.USER_PASSWORD_CHANGED})

    @action(
        methods=['post'],
        detail=False,
        serializer_class=ForgotPasswordSerializer,
        permission_classes=(),
        url_path='forgot-password'
    )
    def forgot_password(self, request):
        serializer = self.serializer_class(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        OTPCode.create_otp_from(validated_data['email'])
        return Response({'message': messages.USER_OTP_SENT})
    
    @action(
        methods=['post'],
        detail=False,
        serializer_class=ForgotPasswordVerifySerializer,
        permission_classes=(),
        url_path='forgot-password-verify',
    )
    def forgot_password_verify(self, request):
        serializer = self.serializer_class(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        OTPCode.claim(validated_data['code'], validated_data['identifier'])
        user = User.get_from_email(validated_data['identifier'], raise_exception=True)
        user.set_new_password(validated_data['new_password'])

        return Response({'message': messages.USER_PASSWORD_CHANGED})

class OTPView(GenericViewSet):
    permission_classes = ()
    serializer_class = OTPSerializer

    @action(
        methods=['post'],
        detail=False,
        serializer_class=SendOTPSerializer,
    )
    def send(self, request):
        serializer = self.serializer_class(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        OTPCode.create_otp_from(validated_data['identifier'])
        return Response({'message': messages.USER_OTP_SENT}, status=status.HTTP_201_CREATED)

    @action(
        methods=['post'],
        detail=False,
    )
    def verify(self, request):
        serializer = self.serializer_class(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        OTPCode.verify(validated_data['code'], validated_data['identifier'])
        return Response({'valid': True})


otp_view = OTPView
register_user_view = RegisterUserView
user_view = UserView
