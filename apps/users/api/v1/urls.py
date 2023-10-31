from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.users.api.v1 import views


app_name = 'apps.users.api.v1'

router = DefaultRouter()
router.register('register', views.register_user_view, basename='register')
router.register('otp', views.otp_view, basename='otp')
router.register('', views.user_view, basename='users')

urlpatterns = [
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
urlpatterns += router.urls
