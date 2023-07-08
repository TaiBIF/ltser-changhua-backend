from django.urls import path
from .views import RegisterAPIView, VerifyEmailAPIView, ResendEmailVerifyAPIView, LoginAPIView, UserProfileAPIView, \
    UserProfileUpdateAPIView, UpdateUserPasswordAPIView

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('signUp/', RegisterAPIView.as_view(), name='sign-up'),
    path('email-verify/', VerifyEmailAPIView.as_view(), name='email-verify'),
    path('resend-email-verify/', ResendEmailVerifyAPIView.as_view(), name='resend-email-verify'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('getUserProfile/', UserProfileAPIView.as_view(), name='getUserProfile'),
    path('updateUserProfile/', UserProfileUpdateAPIView.as_view(), name="update_user_profile"),
    path('updateUserPassword/', UpdateUserPasswordAPIView.as_view(), name='update-user-password'),
]