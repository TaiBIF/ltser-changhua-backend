from django.urls import path
from .views import RegisterAPIView, VerifyEmailAPIView, ResendEmailVerifyAPIView

urlpatterns = [
    path('signUp/', RegisterAPIView.as_view(), name='sign-up'),
    path('email-verify/', VerifyEmailAPIView.as_view(), name='email-verify'),
    path('resend-email-verify/', ResendEmailVerifyAPIView.as_view(), name='resend-email-verify'),
]