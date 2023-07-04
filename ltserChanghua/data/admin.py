from django.contrib import admin
from .models import HomepagePhoto

class HomepagePhotoAdmin(admin.ModelAdmin):
    list_display = ('order', 'image', 'display')

admin.site.register(HomepagePhoto, HomepagePhotoAdmin)