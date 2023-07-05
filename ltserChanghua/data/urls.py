from django.urls import path
from .views import HomepagePhotoAPIView, LatestEventAPIView

urlpatterns = [
    path("getHomepagePhotos", HomepagePhotoAPIView.as_view(), name="getHomepagePhotos"),
    path("getLatestEvents", LatestEventAPIView.as_view(), name="getLatestEvents"),
]