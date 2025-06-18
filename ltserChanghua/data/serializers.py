from .models import (
    HomepagePhoto,
    LatestEvent,
    LatestEventTag,
    CrabSite,
    WaterQualityManualSite,
    BenthicOrganismData,
    CrabData,
    Literature,
    NewsTag,
    News,
    ResearchTag,
    Research,
    InterviewContent,
    WaterQualityManualData,
    InterviewTag2,
    InterviewTag3,
    Staff,
    InterviewStakeholder,
    InterviewTag1,
    InterviewPeople,
    ResearchesIssue,
)
import re
from rest_framework import serializers
from collections import OrderedDict


class HomepagePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomepagePhoto
        fields = "__all__"


class LatestEventTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatestEventTag
        fields = ["id", "title"]


class LatestEventSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = LatestEvent
        fields = ["id", "title", "activities", "link", "tags", "views"]

    def get_activities(self, obj):
        activities = {
            "reference": obj.organizer,
            "time": obj.activityTime.strftime("%Y/%m/%d %H:%M"),
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
        fields = ["id", "title", "literature", "link", "views"]

    def get_literature(self, obj):
        return {
            "author": obj.author,
            "publisher": obj.publisher,
            "date": obj.date,
            "refId": obj.refID,
        }


class NewsTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsTag
        fields = ("id", "title")


class NewsSerializer(serializers.ModelSerializer):
    news = serializers.SerializerMethodField()
    # tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def get_news(self, obj):
        news_data = {
            "reference": obj.reference,
            "date": obj.date.strftime("%Y-%m-%d"),
            "reporter": obj.reporter,
            "photographer": obj.photographer,
        }
        return news_data

    class Meta:
        model = News
        fields = ("id", "title", "news", "link", "views")


class ResearchTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchTag
        fields = ("id", "title")


class ResearchSerializer(serializers.ModelSerializer):
    research = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def get_research(self, obj):
        resarch_data = {
            "author": obj.author,
            "year": obj.year,
            "reference": obj.reference,
        }
        return resarch_data

    class Meta:
        model = Research
        fields = ("id", "title", "research", "link", "tags", "views")


class InterviewContentSerializer(serializers.ModelSerializer):
    content = serializers.SerializerMethodField()
    date = serializers.DateField(source="interview_date")
    tag2 = serializers.SlugRelatedField(
        slug_field="title", source="interview_tag2", many=True, read_only=True
    )
    tag3 = serializers.SlugRelatedField(
        slug_field="title", source="interview_tag3", many=True, read_only=True
    )
    people = serializers.SlugRelatedField(
        slug_field="title", source="interview_people", many=True, read_only=True
    )
    stakeholder = serializers.SlugRelatedField(
        slug_field="title", source="interview_stakeholder", many=True, read_only=True
    )

    class Meta:
        model = InterviewContent
        fields = ["id", "date", "content", "tag2", "tag3", "people", "stakeholder"]

    def get_content(self, obj):
        request = self.context.get("request")
        if (
            request
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.is_applied)
        ):
            return obj.content
        return obj.content[:20] + "......"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        searched_tags = request.query_params.get("tag3", "").split(",")

        tag2_objects = [
            {"tag_type": "tag2", "id": obj.id, "title": obj.title}
            for obj in instance.interview_tag2.all()
        ]
        tag3_objects = [
            {"tag_type": "tag3", "id": obj.id, "title": obj.title}
            for obj in instance.interview_tag3.all()
        ]
        combined_tags = tag2_objects + tag3_objects

        def sort_key(tag):
            title = tag["title"]
            if title in searched_tags:
                return (0,)
            if title.startswith("0.1."):
                return (2,)

            numbers = re.findall(r"\d+", title)
            return (1,) + tuple(map(int, numbers))

        representation["combined_tags"] = sorted(combined_tags, key=sort_key)

        representation["combined_tags"] = [
            {tag["tag_type"]: tag["id"], "title": tag["title"]}
            for tag in representation["combined_tags"]
        ]

        del representation["tag2"]
        del representation["tag3"]
        return representation


class InterviewTag2Serializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewTag2
        fields = ["id", "title", "interview_tag1_id"]


class InterviewTag3Serializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewTag3
        fields = ["id", "title"]


class InterviewStakeholderSerializer(serializers.ModelSerializer):
    stakeholder = serializers.IntegerField(source="id")
    categoryId = serializers.SerializerMethodField()
    groupId = serializers.SerializerMethodField()
    people = serializers.SerializerMethodField()

    class Meta:
        model = InterviewStakeholder
        fields = ["stakeholder", "categoryId", "groupId", "optionId", "title", "people"]

    def get_categoryId(self, obj):
        return "0"

    def get_groupId(self, obj):
        return None

    def get_people(self, obj):
        people_titles = (
            InterviewPeople.objects.filter(interview_stakeholder=obj)
            .order_by("order")
            .values_list("title", flat=True)
        )
        return list(people_titles)


class InterviewTag1Serializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewTag1
        fields = ["id", "title"]


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = "__all__"


class ResearchesIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchesIssue
        fields = "__all__"
