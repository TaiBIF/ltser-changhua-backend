from django.contrib import admin
from .models import HomepagePhoto, LatestEvent, LatestEventTag, CrabSite, WaterQualityManualSite, InterviewTag1, \
    InterviewTag2, InterviewTag3, InterviewStakeholder, InterviewPeople, InterviewContent, Literature, NewsTag, News,\
    ResearchTag, Research, WaterQualityManualData, BenthicOrganismData

class HomepagePhotoAdmin(admin.ModelAdmin):
    list_display = ('order', 'image', 'display')

class LatestEventTagAdmin(admin.ModelAdmin):
    list_display = ['title']

class LatestEventAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'url', 'organizer', 'activityTime', 'display']
    list_filter = ['display', 'created_at', 'updated_at']
    search_fields = ['title', 'organizer']
    raw_id_fields = ['tags']

class BenthicOrganismDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'site', 'month']

class CrabSiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'latitude', 'longitude']


class WaterQualityManualSiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'latitude', 'longitude']

class WaterQualityManualDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'year', 'site', 'month']

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

class LiteratureAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'publisher', 'date', 'is_ebook', 'views']

class NewsTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'reference', 'reporter', 'photographer', 'date', 'link', 'views')
    list_filter = ('date',)
    search_fields = ('title', 'reference', 'reporter')
    ordering = ('-date',)

class ResearchTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

class ResearchAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'year', 'reference', 'link', 'display_research_tag', 'views')
    ordering = ('-year',)

    def display_research_tag(self, obj):
        return ', '.join([tag.title for tag in obj.tags.all()])

admin.site.register(HomepagePhoto, HomepagePhotoAdmin)
admin.site.register(LatestEventTag, LatestEventTagAdmin)
admin.site.register(LatestEvent, LatestEventAdmin)
admin.site.register(CrabSite, CrabSiteAdmin)
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