from django.contrib import admin
from .models import MyUser, UserProfile, DownloadRecord
from django import forms
from datetime import timedelta
import csv
from django.http import HttpResponse
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

class MyUserForm(forms.ModelForm):
    class Meta:
        model = MyUser
        exclude = ['password']
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 1


class MyUserAdmin(admin.ModelAdmin):
    form = MyUserForm
    list_display = (
    'id', 'get_email', 'get_name', 'get_verified', 'get_groups', 'get_school', 'get_location', 'get_department',
    'get_title', 'get_category', 'get_application', 'get_attention')
    inlines = [UserProfileInline]
    readonly_fields = ('email', 'username')
    search_fields = ['email']
    actions = ['export_as_csv']

    def get_email(self, obj):
        return obj.email

    def get_verified(self, obj):
        return obj.is_verified

    get_verified.admin_order_field = 'is_verified'

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    def get_name(self, obj):
        return obj.last_name + obj.first_name


    def get_school(self, obj):
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.school
        return ''

    def get_location(self, obj):
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.location
        return ''

    def get_department(self, obj):
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.department
        return ''

    def get_title(self, obj):
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.title
        return ''

    def get_category(self, obj):
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.category
        return ''

    def get_application(self, obj):
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.application
        return ''

    def get_attention(self, obj):
        if hasattr(obj, 'userprofile'):
            return obj.userprofile.attention
        return ''

    def export_as_csv(self, request, queryset):
        fields = ['id', 'email', 'get_name', 'is_verified', 'get_groups'
                  'school', 'location', 'department', 'title', 'category',
                  'application', 'attention', ]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Email', 'Name', 'Is Verified', 'Groups',
                         'School', 'Location', 'Department', 'Title', 'Category',
                         'Application', 'Attention'])

        for obj in queryset:
            row = []
            for field in fields:
                if field in ['school', 'location', 'department', 'title',
                             'category', 'application', 'attention']:
                    if hasattr(obj, 'userprofile'):
                        row.append(getattr(obj.userprofile, field) or '')
                    else:
                        row.append('')
                elif hasattr(obj, field):
                    row.append(getattr(obj, field) or '')
                elif hasattr(self, field):  # 检查是否是方法
                    row.append(getattr(self, field)(obj) or '')
                else:
                    row.append('')
            writer.writerow(row)
        return response

    export_as_csv.short_description = "輸出會員資料"
    get_email.short_description = 'email'
    get_verified.short_description = 'verified'
    get_name.short_description = 'name'
    get_groups.short_description = 'groups'
    #get_last_login.short_description = 'last login'
    get_school.short_description = 'school'
    get_location.short_description = 'location'
    get_department.short_description = 'department'
    get_title.short_description = 'title'
    get_category.short_description = 'category'
    get_application.short_description = 'application'
    get_attention.short_description = 'attention'


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
admin.site.index_template = 'custom_admin_template.html'