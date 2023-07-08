from .models import HomepagePhoto, LatestEvent, LatestEventTag, CrabSite, WaterQualityManualSite, BenthicOrganism, Crab, WaterQualityManual
from rest_framework import serializers

class HomepagePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepagePhoto
        fields = "__all__"

class LatestEventTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatestEventTag
        fields = ['id', 'title']

class LatestEventSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = LatestEvent
        fields = ['id', 'title', 'activities', 'link', 'tags', 'views']

    def get_activities(self, obj):
        activities = {
            'reference': obj.organizer,
            'time': obj.activityTime.strftime('%Y/%m/%d %H:%M')
        }
        return activities

    def get_link(self, obj):
        return obj.url

    def get_tags(self, obj):
        tags = [{'id': tag.id, 'title': tag.title} for tag in obj.tags.all()]
        return tags


class CrabSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrabSite
        fields = "__all__"

class WaterQualityManualSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterQualityManualSite
        fields = "__all__"

class BenthicOrganismSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenthicOrganism
        fields = "__all__"

class CrabSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crab
        fields = "__all__"

class WaterQualityManualSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterQualityManual
        fields = "__all__"