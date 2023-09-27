from django.urls import path
from .views import HomepagePhotoAPIView, LatestEventTagAPIView, LatestEventAPIView, CrabSiteAPIView, \
    WaterQualityManualSiteAPIView, BenthicOrganismAPIView, CrabAPIView, \
    LiteratureAPIView, NewsAPIView, ResearchAPIView, DownloadWaterQualityManyalAPIView, DownloadCrabAPIView, \
    InterviewSingleAPIView, InterviewMultipleAPIView, WaterQualityManualsAPIView, InterviewTag2ListAPIView, \
    InterviewTag3ListAPIView, DownloadInterviewSingleAPIView, DownloadInterviewMultipleAPIView, StaffAPIView, \
    InterviewStakeholderListAPIView, InterviewTag1ListAPIView
urlpatterns = [
    path("getHomepagePhotos", HomepagePhotoAPIView.as_view(), name="getHomepagePhotos"),
    path("getLatestEventsTags", LatestEventTagAPIView.as_view(), name="getLatestEventTags"),
    path("latestEvents/", LatestEventAPIView.as_view(), name="getLatestEvents"),
    path("latestEvents/<str:pk>/", LatestEventAPIView.as_view(), name="latest_events_detail"),
    path("getCrabSites", CrabSiteAPIView.as_view(), name="getCrabSites"),
    path("getWaterQualityManualSites/", WaterQualityManualSiteAPIView.as_view(), name="getWaterQualitySites"),
    path("getBenthicOrganisms",  BenthicOrganismAPIView.as_view(), name="getBenthicOrganisms"),
    path("getCrabs", CrabAPIView.as_view(), name="getCrabs"),
    path("getWaterQualityManuals/", WaterQualityManualsAPIView.as_view(), name="getWaterQualityManuals"),
    path('literatures/', LiteratureAPIView.as_view(), name='get_literature_lists'),
    path('literatures/<str:pk>/', LiteratureAPIView.as_view(), name='literature_detail'),
    path('news/', NewsAPIView.as_view(), name='get_news_lists'),
    path('news/<str:pk>/', NewsAPIView.as_view(), name='news_detail'),
    path('interview-single/', InterviewSingleAPIView.as_view(), name='interview-single'),
    path('interview-multiple/', InterviewMultipleAPIView.as_view(), name='interview-multiple'),
    path('research/', ResearchAPIView.as_view(), name='get_research_lists'),
    path('research/<str:pk>/', ResearchAPIView.as_view(), name='research_detail'),
    path('download/waterQualityManual/', DownloadWaterQualityManyalAPIView.as_view(),
         name='download-waterquality-manual'),
    path('download/crab/', DownloadCrabAPIView.as_view(),
         name='download-crab'),
    path('interview-multiple/stakeholder/', InterviewStakeholderListAPIView.as_view(),
         name='interview-stakeholder-list'),
    path('interview-multiple/tag1/', InterviewTag1ListAPIView.as_view(), name='interview-tag1-list'),
    path('interview-multiple/tag2/', InterviewTag2ListAPIView.as_view(), name='interview-tag2-list'),
    path('interview-multiple/tag3/', InterviewTag3ListAPIView.as_view(), name='interview-tag3-list'),
    path('download/interview-single/', DownloadInterviewSingleAPIView.as_view(), name='download-interview-single'),
    path('download/interview-multiple/', DownloadInterviewMultipleAPIView.as_view(),
         name='download-interview-multiple'),
    path("staff/", StaffAPIView.as_view(), name="get_staff"),

]