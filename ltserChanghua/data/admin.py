from django.contrib import admin
from .models import HomepagePhoto, LatestEvent, Tag

class HomepagePhotoAdmin(admin.ModelAdmin):
    list_display = ('order', 'image', 'display')

class TagAdmin(admin.ModelAdmin):
    list_display = ['title']



class LatestEventAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'url', 'organizer', 'activityTime', 'display']
    list_filter = ['display', 'created_at', 'updated_at']
    search_fields = ['title', 'organizer']
    raw_id_fields = ['tags']


admin.site.register(HomepagePhoto, HomepagePhotoAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(LatestEvent, LatestEventAdmin)
