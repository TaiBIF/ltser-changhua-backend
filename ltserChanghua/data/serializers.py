from .models import HomepagePhoto, LatestEvent, Tag, CrabSite, WaterQualityManualSite, BenthicOrganism, Crab
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
    activities = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = LatestEvent
        fields = ['id', 'title', 'activities', 'link', 'tags', 'views']

    def get_activities(self, obj):
        # 自定義要返回的活動資訊格式
        activities = {
            'reference': obj.organizer,
            'time': obj.activityTime.strftime('%Y/%m/%d %H:%M')  # 更改時間格式
        }
        return activities

    def get_link(self, obj):
        # 返回url作為link
        return obj.url

    def get_tags(self, obj):
        # 返回只有標籤標題的列表
        return [tag.title for tag in obj.tags.all()]


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