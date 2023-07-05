from django.urls import path
from .views import HomepagePhotoAPIView, LatestEventAPIView, ChangeLatestEventViewsAPIView, CrabSiteAPIView, WaterQualityManualSiteAPIView

urlpatterns = [
    path("getHomepagePhotos", HomepagePhotoAPIView.as_view(), name="getHomepagePhotos"),
    path("getLatestEvents", LatestEventAPIView.as_view(), name="getLatestEvents"),
    path("changeLatestEventViews/<str:pk>", ChangeLatestEventViewsAPIView.as_view(), name="changeLatestEventViews"),
    path("getCrabSites", CrabSiteAPIView.as_view(), name="getCrabSites"),
    path("getWaterQualityManualSites", WaterQualityManualSiteAPIView.as_view(), name="getWaterQualitySites"),
]