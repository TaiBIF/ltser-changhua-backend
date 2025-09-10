from django.contrib import admin
from .models import (
    HomepagePhoto,
    LatestEvent,
    LatestEventTag,
    CrabSite,
    WaterQualityManualSite,
    InterviewTag1,
    InterviewTag2,
    InterviewTag3,
    InterviewStakeholder,
    InterviewPeople,
    InterviewContent,
    Literature,
    NewsTag,
    News,
    ResearchTag,
    Research,
    WaterQualityManualData,
    BenthicOrganismData,
    CrabData,
    Staff,
    ResearchesIssue,
    OysterFarmingStats,
    FisheryFarmingStats,
)
from .resources import OysterFarmingStatsResource, FisheryFarmingStatsResource
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.template.defaultfilters import truncatechars
from import_export.widgets import ManyToManyWidget
from datetime import datetime
from import_export.widgets import DateWidget
from django.core.exceptions import ObjectDoesNotExist
import csv
from django.http import HttpResponse


class HomepagePhotoAdmin(admin.ModelAdmin):
    list_display = ("order", "image", "display")
    search_fields = ["image"]


class LatestEventTagAdmin(admin.ModelAdmin):
    list_display = ["title"]
    search_fields = ["title"]


class LatestEventAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "url", "organizer", "activityTime", "display"]
    list_filter = ["display", "created_at", "updated_at"]
    search_fields = ["title", "organizer"]
    raw_id_fields = ["tags"]


class BenthicOrganismDataResource(resources.ModelResource):
    class Meta:
        model = BenthicOrganismData


class BenthicOrganismDataAdmin(ImportExportModelAdmin):
    resource_class = BenthicOrganismDataResource
    list_display = (
        "year",
        "site",
        "month",
        "cw",
        "mm",
        "sc",
        "co",
        "s_temp",
        "t_sal",
        "s_ph",
        "w_temp",
        "w_ph",
        "cond",
        "do",
        "w_sal",
        "tds",
        "turb",
        "orp",
    )


class CrabSiteAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "latitude", "longitude"]
    search_fields = ["title"]


class StaffAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "name", "duty", "email", "order"]
    search_fields = ["title"]


class WaterQualityManualSiteAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "latitude", "longitude"]
    search_fields = ["title"]


class WaterQualityManualDataResource(resources.ModelResource):
    class Meta:
        model = WaterQualityManualData


class WaterQualityManualDataAdmin(ImportExportModelAdmin):
    resource_class = WaterQualityManualDataResource
    list_display = (
        "year",
        "site",
        "month",
        "w_temp",
        "w_ph",
        "phmv",
        "orp",
        "cond",
        "turb",
        "do",
        "tds",
        "w_sal",
        "sg",
    )


class InterviewTag1Admin(admin.ModelAdmin):
    list_display = ["id", "title", "order"]
    search_fields = ["title"]


class InterviewTag2Admin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "interview_tag1",
        "order",
        "search_volume",
        "download_volume",
    ]
    search_fields = ["title"]

    def interview_tag1(self, obj):
        return obj.interview_tag1.title


class InterviewTag3Admin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "interview_tag2",
        "order",
        "search_volume",
        "download_volume",
    ]
    search_fields = ["title"]

    def interview_tag2(self, obj):
        return obj.interview_tag2.title


class InterviewStakeholderAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "order", "optionId"]
    search_fields = ["title"]


class InterviewPeopleAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "interview_stakeholder", "order"]
    search_fields = ["title"]

    def interview_stakeholder(self, obj):
        return obj.interview_stakeholder.title


class InterviewContentResource(resources.ModelResource):
    interview_tag2 = fields.Field(
        column_name="interview_tag2",
        attribute="interview_tag2",
        widget=ManyToManyWidget(InterviewTag2, separator=",", field="title"),
    )
    interview_tag3 = fields.Field(
        column_name="interview_tag3",
        attribute="interview_tag3",
        widget=ManyToManyWidget(InterviewTag3, separator=",", field="title"),
    )
    interview_people = fields.Field(
        column_name="interview_people",
        attribute="interview_people",
        widget=ManyToManyWidget(InterviewPeople, ",", "title"),
    )
    interview_stakeholder = fields.Field(
        column_name="interview_stakeholder",
        attribute="interview_stakeholder",
        widget=ManyToManyWidget(InterviewStakeholder, ",", "title"),
    )

    class Meta:
        model = InterviewContent
        fields = (
            "content",
            "interview_tag2",
            "interview_tag3",
            "interview_date",
            "interview_people",
            "interview_stakeholder",
        )
        import_id_fields = []

    def before_import_row(self, row, **kwargs):
        date_str = row.get("interview_date")
        if date_str:
            date_obj = datetime.strptime(date_str, "%Y/%m/%d").date()
            row["interview_date"] = date_obj.isoformat()

        interview_tag2 = row.get("interview_tag2")
        if interview_tag2:
            tag_list = [tag.strip() for tag in interview_tag2.split(",")]
            for tag_title in tag_list:
                InterviewTag2.objects.get_or_create(title=tag_title)

        interview_tag3 = row.get("interview_tag3")
        if interview_tag3:
            tag_list = [tag.strip() for tag in interview_tag3.split(",")]
            for tag_title in tag_list:
                InterviewTag3.objects.get_or_create(title=tag_title)


class InterviewContentAdmin(ImportExportModelAdmin):
    resource_class = InterviewContentResource
    list_display = (
        "id",
        "content",
        "interview_date",
        "display_tag2_titles",
        "display_tag3_titles",
        "display_people_names",
        "display_stakeholder_names",
    )
    search_fields = ["content", "interview_date"]

    def display_tag2_titles(self, obj):
        return ", ".join(tag.title for tag in obj.interview_tag2.all())

    display_tag2_titles.short_description = "Tag2 Titles"

    def display_tag3_titles(self, obj):
        return ", ".join(tag.title for tag in obj.interview_tag3.all())

    display_tag3_titles.short_description = "Tag3 Titles"

    def display_people_names(self, obj):
        return ", ".join(people.title for people in obj.interview_people.all())

    display_people_names.short_description = "People Names"

    def display_stakeholder_names(self, obj):
        return ", ".join(
            stakeholder.title for stakeholder in obj.interview_stakeholder.all()
        )

    display_stakeholder_names.short_description = "Stakeholder Names"


class LiteratureResource(resources.ModelResource):
    class Meta:
        model = Literature


class LiteratureAdmin(ImportExportModelAdmin):
    resource_class = LiteratureResource
    list_display = (
        "id",
        "truncated_title",
        "truncated_author",
        "publisher",
        "date",
        "refID",
        "truncated_link",
        "is_ebook",
        "views",
    )

    search_fields = ["title", "author", "publisher", "date"]

    def truncated_title(self, obj):
        return truncatechars(obj.title, 10)

    def truncated_author(self, obj):
        return truncatechars(obj.author, 10)

    def truncated_link(self, obj):
        return truncatechars(obj.link, 10)

    truncated_title.short_description = "Title"
    truncated_author.short_description = "Author"
    truncated_link.short_description = "Link"


class NewsTagAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]


class NewsResource(resources.ModelResource):
    tags = fields.Field(
        column_name="tags",
        attribute="tags",
        widget=ManyToManyWidget(NewsTag, ",", "title"),
    )

    class Meta:
        model = News
        fields = (
            "title",
            "reference",
            "reporter",
            "photographer",
            "date",
            "link",
            "views",
            "tags",
        )
        import_id_fields = []

    def before_import_row(self, row, **kwargs):
        date_str = row.get("date")
        if date_str:
            date_obj = datetime.strptime(date_str, "%Y/%m/%d").date()
            row["date"] = date_obj.isoformat()

        tags = row.get("tags")
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            for tag_title in tag_list:
                NewsTag.objects.get_or_create(title=tag_title)


class NewsAdmin(ImportExportModelAdmin):
    resource_class = NewsResource
    list_display = (
        "id",
        "title",
        "reference",
        "reporter",
        "photographer",
        "date",
        "link",
        "views",
        "display_tags",
    )
    search_fields = ["title", "reference", "reporter", "photographer"]

    def display_tags(self, obj):
        return ", ".join([tag.title for tag in obj.tags.all()])

    display_tags.short_description = "Tags"


class ResearchTagAdmin(admin.ModelAdmin):
    list_display = ["id", "title"]


class ResearchResource(resources.ModelResource):
    tags = fields.Field(
        column_name="tags",
        attribute="tags",
        widget=ManyToManyWidget(ResearchTag, ",", "title"),
    )

    class Meta:
        model = Research
        fields = ("title", "author", "year", "reference", "link", "views", "tags")
        import_id_fields = []  # 這樣可以讓 'id' 變為非必需

    def before_import_row(self, row, **kwargs):
        tags = row.get("tags")
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
            for tag_title in tag_list:
                ResearchTag.objects.get_or_create(title=tag_title)


class ResearchAdmin(ImportExportModelAdmin):
    resource_class = ResearchResource
    list_display = (
        "id",
        "truncated_title",
        "author",
        "year",
        "truncated_reference",
        "truncated_link",
        "views",
        "display_tags",
    )
    search_fields = ["title", "author", "year", "reference"]

    def truncated_title(self, obj):
        return truncatechars(obj.title, 10)

    def truncated_reference(self, obj):
        return truncatechars(obj.reference, 10)

    def truncated_link(self, obj):
        return truncatechars(obj.link, 10)

    def display_tags(self, obj):
        return ", ".join([tag.title for tag in obj.tags.all()])

    display_tags.short_description = "Tags"
    truncated_title.short_description = "Title"
    truncated_reference.short_description = "Reference"
    truncated_link.short_description = "Link"


class CrabDataResource(resources.ModelResource):
    class Meta:
        model = CrabData


class CrabDataAdmin(ImportExportModelAdmin):
    resource_class = CrabDataResource
    list_display = (
        "year",
        "site",
        "month",
        "Mbr",
        "Mb",
        "Ma",
        "Hf",
        "Hd",
        "Hp",
        "Me",
        "Sb",
        "Sl",
        "It",
        "Oc",
        "Al",
        "Ta",
        "Gb",
        "Xf",
        "Pa",
        "Pp",
        "Tc",
        "Ppi",
        "Mv",
        "Charybids_sp",
        "Mt",
        "Pb",
        "Mth",
    )


class ResearchesIssueResource(resources.ModelResource):
    class Meta:
        model = ResearchesIssue


class ResearchesIssueAdmin(ImportExportModelAdmin):
    resource_class = ResearchesIssueResource
    list_display = ("id", "title", "identity", "is_display", "hits")
    search_fields = ("title", "identity")
    list_filter = ("is_display", "identity")
    ordering = ("id",)
    readonly_fields = ("hits",)


class OysterFarmingStatsAdmin(ImportExportModelAdmin):
    resource_class = OysterFarmingStatsResource
    list_display = ("id", "year")
    ordering = ("year",)

    fieldsets = (
        ("基本資訊", {"fields": ("year",)}),
        (
            "平掛式",
            {
                "fields": (
                    "horizontal_facilities_nation",
                    "horizontal_farmers_nation",
                    "horizontal_facilities_changhua",
                    "horizontal_farmers_changhua",
                    "horizontal_facilities_fangyuan",
                    "horizontal_farmers_fangyuan",
                )
            },
        ),
        (
            "插篊式",
            {
                "fields": (
                    "stake_facilities_nation",
                    "stake_farmers_nation",
                    "stake_facilities_changhua",
                    "stake_farmers_changhua",
                    "stake_facilities_fangyuan",
                    "stake_farmers_fangyuan",
                )
            },
        ),
        (
            "垂下式",
            {
                "fields": (
                    "hanging_facilities_nation",
                    "hanging_farmers_nation",
                    "hanging_facilities_changhua",
                    "hanging_farmers_changhua",
                    "hanging_facilities_fangyuan",
                    "hanging_farmers_fangyuan",
                )
            },
        ),
        (
            "浮筏式",
            {
                "fields": (
                    "raft_facilities_nation",
                    "raft_farmers_nation",
                    "raft_facilities_changhua",
                    "raft_farmers_changhua",
                    "raft_facilities_fangyuan",
                    "raft_farmers_fangyuan",
                )
            },
        ),
        (
            "延繩式",
            {
                "fields": (
                    "longline_facilities_nation",
                    "longline_farmers_nation",
                    "longline_facilities_changhua",
                    "longline_farmers_changhua",
                    "longline_facilities_fangyuan",
                    "longline_farmers_fangyuan",
                )
            },
        ),
        (
            "申報（調查）總戶數",
            {
                "fields": (
                    "total_farmers_nation",
                    "total_farmers_changhua",
                    "total_farmers_fangyuan",
                )
            },
        ),
    )


class FisheryFarmingStatsAdmin(ImportExportModelAdmin):
    resource_class = FisheryFarmingStatsResource
    list_display = ("id", "year")
    ordering = ("year",)

    fieldsets = (
        ("基本資訊", {"fields": ("year",)}),
        (
            "文蛤",
            {
                "fields": (
                    "hard_clam_households_total",
                    "hard_clam_area_hectare",
                    "hard_clam_stocking_in_pond",
                    "hard_clam_stocking_new",
                    "hard_clam_hatchery_households",
                    "hard_clam_farmer_households",
                )
            },
        ),
        (
            "烏魚",
            {
                "fields": (
                    "mullet_households_total",
                    "mullet_area_hectare",
                    "mullet_stocking_in_pond",
                    "mullet_stocking_new",
                    "mullet_hatchery_households",
                    "mullet_farmer_households",
                )
            },
        ),
        (
            "虱目魚",
            {
                "fields": (
                    "milkfish_households_total",
                    "milkfish_area_hectare",
                    "milkfish_stocking_in_pond",
                    "milkfish_stocking_new",
                    "milkfish_hatchery_households",
                    "milkfish_farmer_households",
                )
            },
        ),
        (
            "蜆",
            {
                "fields": (
                    "asiatic_clam_households_total",
                    "asiatic_clam_area_hectare",
                    "asiatic_clam_stocking_in_pond",
                    "asiatic_clam_stocking_new",
                    "asiatic_clam_hatchery_households",
                    "asiatic_clam_farmer_households",
                )
            },
        ),
        (
            "白蝦",
            {
                "fields": (
                    "white_shrimp_households_total",
                    "white_shrimp_area_hectare",
                    "white_shrimp_stocking_in_pond",
                    "white_shrimp_stocking_new",
                    "white_shrimp_hatchery_households",
                    "white_shrimp_farmer_households",
                )
            },
        ),
        (
            "吳郭魚",
            {
                "fields": (
                    "tilapia_households_total",
                    "tilapia_area_hectare",
                    "tilapia_stocking_in_pond",
                    "tilapia_stocking_new",
                    "tilapia_hatchery_households",
                    "tilapia_farmer_households",
                )
            },
        ),
        (
            "鰻魚",
            {
                "fields": (
                    "eel_households_total",
                    "eel_area_hectare",
                    "eel_stocking_in_pond",
                    "eel_stocking_new",
                    "eel_hatchery_households",
                    "eel_farmer_households",
                )
            },
        ),
        (
            "日本黑蜆",
            {
                "fields": (
                    "yamato_clam_households_total",
                    "yamato_clam_area_hectare",
                    "yamato_clam_stocking_in_pond",
                    "yamato_clam_stocking_new",
                    "yamato_clam_hatchery_households",
                    "yamato_clam_farmer_households",
                )
            },
        ),
        (
            "西施貝",
            {
                "fields": (
                    "purple_clam_households_total",
                    "purple_clam_area_hectare",
                    "purple_clam_stocking_in_pond",
                    "purple_clam_stocking_new",
                    "purple_clam_hatchery_households",
                    "purple_clam_farmer_households",
                )
            },
        ),
    )


admin.site.register(HomepagePhoto, HomepagePhotoAdmin)
admin.site.register(LatestEventTag, LatestEventTagAdmin)
admin.site.register(LatestEvent, LatestEventAdmin)
admin.site.register(CrabSite, CrabSiteAdmin)
admin.site.register(CrabData, CrabDataAdmin)
admin.site.register(WaterQualityManualSite, WaterQualityManualSiteAdmin)
admin.site.register(InterviewTag1, InterviewTag1Admin)
admin.site.register(InterviewTag2, InterviewTag2Admin)
admin.site.register(InterviewTag3, InterviewTag3Admin)
admin.site.register(InterviewStakeholder, InterviewStakeholderAdmin)
admin.site.register(InterviewPeople, InterviewPeopleAdmin)
admin.site.register(InterviewContent, InterviewContentAdmin)
admin.site.register(Literature, LiteratureAdmin)
admin.site.register(NewsTag, NewsTagAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(ResearchTag, ResearchTagAdmin)
admin.site.register(Research, ResearchAdmin)
admin.site.register(WaterQualityManualData, WaterQualityManualDataAdmin)
admin.site.register(BenthicOrganismData, BenthicOrganismDataAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(ResearchesIssue, ResearchesIssueAdmin)
admin.site.register(OysterFarmingStats, OysterFarmingStatsAdmin)
admin.site.register(FisheryFarmingStats, FisheryFarmingStatsAdmin)
