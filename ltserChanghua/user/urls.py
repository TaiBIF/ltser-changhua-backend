from django.urls import path
from .views import RegisterAPIView

urlpatterns = [
    path('signUp/', RegisterAPIView.as_view(), name='sign-up'),
]