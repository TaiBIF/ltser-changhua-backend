from django.urls import path
from .views import RegisterAPIView, VerifyEmailAPIView, ResendEmailVerifyAPIView, LoginAPIView, UserProfileAPIView

urlpatterns = [
    path('signUp/', RegisterAPIView.as_view(), name='sign-up'),
    path('email-verify/', VerifyEmailAPIView.as_view(), name='email-verify'),
    path('resend-email-verify/', ResendEmailVerifyAPIView.as_view(), name='resend-email-verify'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('getUserProfile/', UserProfileAPIView.as_view(), name='getUserProfile'),
]