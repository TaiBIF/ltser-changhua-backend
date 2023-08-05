from django.urls import path
from .views import HomepagePhotoAPIView, LatestEventTagAPIView, LatestEventAPIView, CrabSiteAPIView, \
    WaterQualityManualSiteAPIView, BenthicOrganismAPIView, CrabAPIView, WaterQualityManualsAPIView, \
    LiteratureAPIView, NewsAPIView, ResearchAPIView

urlpatterns = [
    path("getHomepagePhotos", HomepagePhotoAPIView.as_view(), name="getHomepagePhotos"),
    path("getLatestEventsTags", LatestEventTagAPIView.as_view(), name="getLatestEventTags"),
    path("latestEvents/", LatestEventAPIView.as_view(), name="getLatestEvents"),
    path("latestEvents/<str:pk>/", LatestEventAPIView.as_view(), name="latest_events_detail"),
    path("getCrabSites", CrabSiteAPIView.as_view(), name="getCrabSites"),
    path("getWaterQualityManualSites", WaterQualityManualSiteAPIView.as_view(), name="getWaterQualitySites"),
    path("getBenthicOrganisms",  BenthicOrganismAPIView.as_view(), name="getBenthicOrganisms"),
    path("getCrabs", CrabAPIView.as_view(), name="getCrabs"),
    path("getWaterQualityManuals", WaterQualityManualsAPIView.as_view(), name="getWaterQualityManuals"),
    path('literatures/', LiteratureAPIView.as_view(), name='get_literature_lists'),
    path('literatures/<str:pk>/', LiteratureAPIView.as_view(), name='literature_detail'),
    path('news/', NewsAPIView.as_view(), name='get_news_lists'),
    path('news/<str:pk>/', NewsAPIView.as_view(), name='news_detail'),
    path('research/', ResearchAPIView.as_view(), name='get_research_lists'),
    path('research/<str:pk>/', ResearchAPIView.as_view(), name='research_detail'),
]