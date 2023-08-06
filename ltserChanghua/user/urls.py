from django.urls import path
from .views import RegisterAPIView, VerifyEmailAPIView, ResendEmailVerifyAPIView, LoginAPIView, UserProfileAPIView, \
    UserProfileUpdateAPIView, UpdateUserPasswordAPIView, RequestPasswordResetEmailAPIView,PasswordTokenCheckAPIView, \
    SetNewPasswordAPIView, DownloadRecordAPIView

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
    path('request-rest-email/', RequestPasswordResetEmailAPIView.as_view(), name='request-rest-email'),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPIView.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
    path('download-record/', DownloadRecordAPIView.as_view(), name='download-record')
]