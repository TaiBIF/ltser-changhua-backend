from django.contrib import admin
from .models import MyUser, UserProfile, DownloadRecord
from django import forms
from datetime import timedelta
import csv
from django.http import HttpResponse

class MyUserForm(forms.ModelForm):
    class Meta:
        model = MyUser
        exclude = ['password']
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 1
class MyUserAdmin(admin.ModelAdmin):
    form = MyUserForm
    list_display = ('id', 'get_email', 'get_name', 'get_verified', 'get_last_login')
    inlines = [UserProfileInline]
    readonly_fields = ('email', 'username')
    search_fields = ['email']
    def get_email(self, obj):
        return obj.email

    def get_verified(self, obj):
        return obj.is_verified

    def get_name(self, obj):
        return obj.last_name + obj.first_name

    def get_last_login(self, obj):
        return obj.last_login

    get_email.short_description = 'EMAIL ADDRESS'
    get_verified.short_description = 'VERIFIED STATUS'
    get_name.short_description = 'NAME'
    get_last_login.short_description = 'LAST LOGIN'


class DownloadRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'filename', 'user', 'display_created_at')
    search_fields = ['user__email', 'filename']
    readonly_fields = ('id', 'filename', 'time', 'user', 'created_at')
    actions = ['export_as_csv']

    def has_add_permission(self, request):
        return False
    def display_created_at(self, obj):
        return obj.created_at + timedelta(hours=8)
    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def export_as_csv(self, request, queryset):
        # 定義 CSV 文件的表頭
        fields = ['filename', 'user', 'created_at']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="download_records.csv"'

        writer = csv.writer(response)
        writer.writerow(fields)

        for obj in queryset:
            created_at = getattr(obj, 'created_at') + timedelta(hours=8)
            writer.writerow([getattr(obj, 'filename'), getattr(obj, 'user'), created_at])

        return response

    export_as_csv.short_description = "輸出下載紀錄"
    display_created_at.short_description = 'Created At'

admin.site.register(MyUser, MyUserAdmin)
admin.site.register(DownloadRecord, DownloadRecordAdmin)
