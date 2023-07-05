from django.urls import path
from .views import HomepagePhotoAPIView, LatestEventAPIView, ChangeLatestEventViewsAPIView, CrabSiteAPIView, \
    WaterQualityManualSiteAPIView, BenthicOrganismAPIView, CrabAPIView, WaterQualityManualsAPIView

urlpatterns = [
    path("getHomepagePhotos", HomepagePhotoAPIView.as_view(), name="getHomepagePhotos"),
    path("getLatestEvents", LatestEventAPIView.as_view(), name="getLatestEvents"),
    path("changeLatestEventViews/<str:pk>", ChangeLatestEventViewsAPIView.as_view(), name="changeLatestEventViews"),
    path("getCrabSites", CrabSiteAPIView.as_view(), name="getCrabSites"),
    path("getWaterQualityManualSites", WaterQualityManualSiteAPIView.as_view(), name="getWaterQualitySites"),
    path("getBenthicOrganisms",  BenthicOrganismAPIView.as_view(), name="getBenthicOrganisms"),
    path("getCrabs", CrabAPIView.as_view(), name="getCrabs"),
    path("getWaterQualityManuals", WaterQualityManualsAPIView.as_view(), name="getWaterQualityManuals"),
]