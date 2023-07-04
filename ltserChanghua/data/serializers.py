from .models import HomepagePhoto
from rest_framework import serializers

class HomepagePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepagePhoto
        fields = "__all__"