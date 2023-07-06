from django.urls import path
from .views import RegisterAPIView, VerifyEmailAPIView

urlpatterns = [
    path('signUp/', RegisterAPIView.as_view(), name='sign-up'),
    path('email-verify/', VerifyEmailAPIView.as_view(), name='email-verify'),
    path('resend-email-verify/', views.ResendEmailVerify.as_view(), name='resend-email-verify'),
]