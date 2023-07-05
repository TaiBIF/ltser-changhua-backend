from .models import HomepagePhoto, LatestEvent, Tag, CrabSite, WaterQualityManualSite
from rest_framework import serializers

class HomepagePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepagePhoto
        fields = "__all__"

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['title']

class LatestEventSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = LatestEvent
        fields = "__all__"


class CrabSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrabSite
        fields = "__all__"

class WaterQualityManualSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterQualityManualSite
        fields = "__all__"