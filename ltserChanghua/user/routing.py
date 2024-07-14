from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("ws/user/<str:email_prefix>/<str:email_suffix>/", MyUserConsumer.as_asgi()),
]