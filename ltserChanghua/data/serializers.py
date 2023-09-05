from .models import HomepagePhoto, LatestEvent, LatestEventTag, CrabSite, WaterQualityManualSite, BenthicOrganismData, \
    CrabData, Literature, NewsTag, News, ResearchTag, Research, InterviewContent, WaterQualityManualData
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
        model = BenthicOrganismData
        fields = "__all__"

class CrabSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrabData
        fields = "__all__"

class WaterQualityManualSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterQualityManualData
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
    research = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def get_research(self, obj):
        resarch_data = {
            'author': obj.author,
            'year': obj.year,
            'reference': obj.reference,
        }
        return resarch_data

    class Meta:
        model = Research
        fields = ('id', 'title', 'research', 'link', 'tags', 'views')

class InterviewContentSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    date = serializers.DateField(source='interview_date')
    tag2 = serializers.SlugRelatedField(slug_field='title', source='interview_tag2', many=True, read_only=True)
    tag3 = serializers.SlugRelatedField(slug_field='title', source='interview_tag3', many=True, read_only=True)
    people = serializers.SlugRelatedField(slug_field='title', source='interview_people', many=True, read_only=True)
    stakeholder = serializers.SlugRelatedField(slug_field='title', source='interview_stakeholder', many=True,
                                               read_only=True)

    class Meta:
        model = InterviewContent
        fields = ['date', 'content', 'tag2', 'tag3', 'people', 'stakeholder']

    def get_content(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return obj.content
        return obj.content[:20] + '......'
