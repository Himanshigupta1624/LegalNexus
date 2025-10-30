from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    RegisterAPIView,
    OTPRequestAPIView,
    OTPVerifyAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
    EmailTokenObtainPairAPIView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterAPIView.as_view(), name='user-register'),
    path('otp/request/', OTPRequestAPIView.as_view(), name='otp-request'),
    path('otp/verify/', OTPVerifyAPIView.as_view(), name='otp-verify'),
    path('password-reset/request/', PasswordResetRequestAPIView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
    path('token/', EmailTokenObtainPairAPIView.as_view(), name='token_obtain_pair'),
]
