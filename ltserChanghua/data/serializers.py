from .models import HomepagePhoto, LatestEvent, LatestEventTag, CrabSite, WaterQualityManualSite, BenthicOrganism, \
    Crab, WaterQualityManual, Literature, NewsTag, News, ResearchTag, Research
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
        tags = [tag.id for tag in obj.tags.all()]
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

class LiteratureSerializer(serializers.ModelSerializer):
    literature = serializers.SerializerMethodField()

    class Meta:
        model = Literature
        fields = ['id', 'title', 'literature', 'link', 'views']

    def get_literature(self, obj):
        return {
            'author': obj.author,
            'publisher': obj.publisher,
            'date': obj.date,
            'refId': obj.refID,
        }


class NewsTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTag
        fields = ('id', 'title')

class NewsSerializer(serializers.ModelSerializer):
    news = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def get_news(self, obj):
        news_data = {
            'reference': obj.reference,
            'date': obj.date.strftime('%Y-%m-%d'),
            'reporter': obj.reporter,
            'photographer': obj.photographer,
        }
        return news_data

    class Meta:
        model = News
        fields = ('id', 'title', 'news', 'link', 'tags', 'views')

class ResearchTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchTag
        fields = ('id', 'title')

class ResearchSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Research
        fields = ('id', 'title', 'author', 'year', 'reference', 'link', 'tags', 'views')