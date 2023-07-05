from .models import HomepagePhoto, LatestEvent, Tag
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
        fields = ['title', 'url', 'organizer', 'activityTime', 'tags', 'views', 'display', 'created_at', 'updated_at']