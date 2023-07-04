from django.urls import path
from .views import HomepagePhotoAPIView

urlpatterns = [
    path("getHomepagePhotos", HomepagePhotoAPIView.as_view(), name="getHomepagePhotos"),
]