from django.contrib import admin
from .models import HomepagePhoto, LatestEvent, LatestEventTag, CrabSite, WaterQualityManualSite, InterviewTag1, \
    InterviewTag2, InterviewTag3, InterviewStakeholder, InterviewPeople, InterviewContent, Literature, NewsTag, News,\
    ResearchTag, Research, WaterQualityManualData, BenthicOrganismData, CrabData
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.template.defaultfilters import truncatechars
from import_export import fields
from import_export.widgets import ManyToManyWidget
from datetime import datetime

class HomepagePhotoAdmin(admin.ModelAdmin):
    list_display = ('order', 'image', 'display')

class LatestEventTagAdmin(admin.ModelAdmin):
    list_display = ['title']

class LatestEventAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'url', 'organizer', 'activityTime', 'display']
    list_filter = ['display', 'created_at', 'updated_at']
    search_fields = ['title', 'organizer']
    raw_id_fields = ['tags']

class BenthicOrganismDataResource(resources.ModelResource):
    class Meta:
        model = BenthicOrganismData
class BenthicOrganismDataAdmin(ImportExportModelAdmin):
    resource_class = BenthicOrganismDataResource
    list_display = (
        'year', 'site', 'month', 'cw', 'mm', 'sc', 'co',
        's_temp', 't_sal', 's_ph', 'w_temp', 'w_ph',
        'cond', 'do', 'w_sal', 'tds', 'turb', 'orp'
    )

class CrabSiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'latitude', 'longitude']


class WaterQualityManualSiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'latitude', 'longitude']

class WaterQualityManualDataResource(resources.ModelResource):
    class Meta:
        model = WaterQualityManualData

class WaterQualityManualDataAdmin(ImportExportModelAdmin):
    resource_class = WaterQualityManualDataResource
    list_display = (
        'year', 'site', 'month', 'w_temp', 'w_ph', 'phmv', 'orp',
        'cond', 'turb', 'do', 'tds', 'w_sal', 'sg'
    )

class InterviewTag1Admin(admin.ModelAdmin):
    list_display = ['id', 'title']

class InterviewTag2Admin(admin.ModelAdmin):
    list_display = ['id', 'title', 'interview_tag1']
    def interview_tag1(self, obj):
        return obj.interview_tag1.title

class InterviewTag3Admin(admin.ModelAdmin):
    list_display = ['id', 'title', 'interview_tag2']
    def interview_tag2(self, obj):
        return obj.interview_tag2.title

class InterviewStakeholderAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

class InterviewPeopleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'interview_stakeholder']

    def interview_stakeholder(self, obj):
        return obj.interview_stakeholder.title

class InterviewContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'content', 'display_interview_tag2', 'display_interview_tag3', 'display_interview_people', 'display_interview_stakeholder']

    def display_interview_tag2(self, obj):
        return ', '.join([tag.title for tag in obj.interview_tag2.all()])

    def display_interview_tag3(self, obj):
        return ', '.join([tag.title for tag in obj.interview_tag3.all()])

    def display_interview_people(self, obj):
        return ', '.join([person.title for person in obj.interview_people.all()])

    def display_interview_stakeholder(self, obj):
        return ', '.join([stakeholder.title for stakeholder in obj.interview_stakeholder.all()])


class LiteratureResource(resources.ModelResource):
    class Meta:
        model = Literature


class LiteratureAdmin(ImportExportModelAdmin):
    resource_class = LiteratureResource
    list_display = ('truncated_title', 'truncated_author', 'publisher', 'date', 'refID', 'truncated_link', 'is_ebook', 'views')

    # 定义其他的设置 ...

    def truncated_title(self, obj):
        return truncatechars(obj.title, 10)

    def truncated_author(self, obj):
        return truncatechars(obj.author, 10)

    def truncated_link(self, obj):
        return truncatechars(obj.link, 10)

    truncated_title.short_description = 'Title'
    truncated_author.short_description = 'Author'
    truncated_link.short_description = 'Link'

class NewsTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']


class NewsResource(resources.ModelResource):
    tags = fields.Field(
        column_name='tags',
        attribute='tags',
        widget=ManyToManyWidget(NewsTag, ',', 'title')
    )
    class Meta:
        model = News
        fields = ('title', 'reference', 'reporter', 'photographer', 'date', 'link', 'views', 'tags')
        import_id_fields = []

    def before_import_row(self, row, **kwargs):
        date_str = row.get('date')
        if date_str:
            date_obj = datetime.strptime(date_str, '%Y/%m/%d').date()
            row['date'] = date_obj.isoformat()

        tags = row.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag_title in tag_list:
                NewsTag.objects.get_or_create(title=tag_title)



class NewsAdmin(ImportExportModelAdmin):
    resource_class = NewsResource
    list_display = ('title', 'reference', 'reporter', 'photographer', 'date', 'link', 'views', 'display_tags')

    def display_tags(self, obj):
        return ", ".join([tag.title for tag in obj.tags.all()])
    display_tags.short_description = 'Tags'

class ResearchTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

class ResearchResource(resources.ModelResource):
    tags = fields.Field(
        column_name='tags',
        attribute='tags',
        widget=ManyToManyWidget(ResearchTag, ',', 'title')
    )

    class Meta:
        model = Research
        fields = ('title', 'author', 'year', 'reference', 'link', 'views', 'tags')
        import_id_fields = []  # 這樣可以讓 'id' 變為非必需

    def before_import_row(self, row, **kwargs):
        tags = row.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag_title in tag_list:
                ResearchTag.objects.get_or_create(title=tag_title)


class ResearchAdmin(ImportExportModelAdmin):
    resource_class = ResearchResource
    list_display = ('truncated_title', 'author', 'year', 'truncated_reference', 'truncated_link', 'views', 'display_tags')

    def truncated_title(self, obj):
        return truncatechars(obj.title, 10)
    def truncated_reference(self, obj):
        return truncatechars(obj.reference, 10)

    def truncated_link(self, obj):
        return truncatechars(obj.link, 10)

    def display_tags(self, obj):
        return ", ".join([tag.title for tag in obj.tags.all()])

    display_tags.short_description = 'Tags'
    truncated_title.short_description = 'Title'
    truncated_reference.short_description = 'Reference'
    truncated_link.short_description = 'Link'


class CrabDataResource(resources.ModelResource):
    class Meta:
        model = CrabData

class CrabDataAdmin(ImportExportModelAdmin):
    resource_class = CrabDataResource
    list_display = (
        'year', 'site', 'month', 'Mbr', 'Mb', 'Ma', 'Hf', 'Hd', 'Hp', 'Me', 'Sb',
        'Sl', 'It', 'Oc', 'Al', 'Ta', 'Gb', 'Xf', 'Pa', 'Pp', 'Tc', 'Ppi',
        'Mv', 'Charybids_sp', 'Mt'
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