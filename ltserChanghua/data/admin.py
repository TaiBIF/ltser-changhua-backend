from django.contrib import admin
from .models import HomepagePhoto, LatestEvent, LatestEventTag, CrabSite, WaterQualityManualSite, InterviewTag1, \
    InterviewTag2, InterviewTag3, InterviewStakeholder, InterviewPeople, InterviewContent

class HomepagePhotoAdmin(admin.ModelAdmin):
    list_display = ('order', 'image', 'display')

class LatestEventTagAdmin(admin.ModelAdmin):
    list_display = ['title']

class LatestEventAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'url', 'organizer', 'activityTime', 'display']
    list_filter = ['display', 'created_at', 'updated_at']
    search_fields = ['title', 'organizer']
    raw_id_fields = ['tags']

class CrabSiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'latitude', 'longitude']


class WaterQualityManualSiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'latitude', 'longitude']

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
    list_display = ['id', 'content', 'interview_tag2', 'interview_tag3', 'interview_people', 'interview_stakeholder']

    def interview_tag2(self, obj):
        return obj.interview_tag2.title

    def interview_tag3(self, obj):
        return obj.interview_tag3.title

    def interview_people(self, obj):
        return obj.interview_people.title

    def interview_stakeholder(self, obj):
        return obj.interview_stakeholder.title


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