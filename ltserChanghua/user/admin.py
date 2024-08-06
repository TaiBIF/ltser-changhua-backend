from django.contrib import admin
from .models import MyUser, UserProfile, DownloadRecord
from django import forms
from datetime import timedelta
import csv
from django.http import HttpResponse
from django.db import models
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html
from django.utils import timezone

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
        'id', 'get_email', 'get_name', 'get_verified', 'get_groups', 'get_last_login', 'get_school', 'get_location',
        'get_department', 'get_title', 'get_category', 'get_application', 'get_attention')
    inlines = [UserProfileInline]
    readonly_fields = ('email', 'username')
    search_fields = ['email']
    actions = ['export_as_csv']

    def get_email(self, obj):
        return obj.email

    def get_verified(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            'red' if not obj.is_verified else 'green',
            '未驗證' if not obj.is_verified else '已驗證'
        )

    get_verified.admin_order_field = 'is_verified'

    def get_groups(self, obj):
        return ", ".join(sorted([group.name for group in obj.groups.all()]))

    def get_last_login(self, obj):
        return obj.last_login.strftime('%Y-%m-%d %H:%M:%S') if obj.last_login else None

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
        fields = ['id', 'email', 'get_name', 'is_verified', 'get_groups',
                  'get_last_login', 'get_school', 'get_location', 'get_department',
                  'get_title', 'get_category', 'get_application', 'get_attention']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="user.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Email', 'Name', 'Is Verified', 'Groups', 'Last Login',
                         'School', 'Location', 'Department', 'Title', 'Category',
                         'Application', 'Attention'])

        for obj in queryset:
            row = []
            for field in fields:
                if hasattr(obj, 'userprofile') and field in ['get_school', 'get_location', 'get_department',
                                                             'get_title', 'get_category', 'get_application',
                                                             'get_attention']:
                    row.append(getattr(obj.userprofile, field[4:]) or '')
                elif hasattr(self, field):
                    row.append(getattr(self, field)(obj) or '')
                elif hasattr(obj, field):
                    row.append(getattr(obj, field) or '')
                else:
                    row.append('')
            writer.writerow(row)
        return response

    export_as_csv.short_description = "輸出會員資料"
    get_email.short_description = 'email'
    get_verified.short_description = 'verified'
    get_name.short_description = 'name'
    get_groups.short_description = 'groups'
    get_last_login.short_description = 'last login'
    get_school.short_description = 'school'
    get_location.short_description = 'location'
    get_department.short_description = 'department'
    get_title.short_description = 'title'
    get_category.short_description = 'category'
    get_application.short_description = 'application'
    get_attention.short_description = 'attention'
    get_groups.admin_order_field = 'groups__name'
    get_last_login.admin_order_field = 'last_login'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['verified_count'] = MyUser.objects.filter(is_verified=True).count()
        extra_context['unverified_count'] = MyUser.objects.filter(is_verified=False).count()
        return super(MyUserAdmin, self).changelist_view(request, extra_context=extra_context)



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

class UserHistory(LogEntry):
    class Meta:
        proxy = True
        verbose_name_plural = '編輯歷程'

class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ('formatted_action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message')
    readonly_fields = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message']

    def get_queryset(self, request):
        return LogEntry.objects.all().select_related('user', 'content_type').order_by('-action_time')

    def formatted_action_time(self, obj):
        adjusted_time = obj.action_time + timedelta(hours=8)
        return adjusted_time.strftime('%Y-%m-%d %H:%M')

    formatted_action_time.admin_order_field = 'action_time'  # Allow sorting by 'action_time'
    formatted_action_time.short_description = 'Action Time'  # Set column header
    def user(self, obj):
        return obj.user

    user.admin_order_field = 'user'
    user.short_description = 'User'

    def content_type(self, obj):
        return obj.content_type

    content_type.admin_order_field = 'content_type'
    content_type.short_description = 'Content Type'

    def object_repr(self, obj):
        return obj.object_repr

    object_repr.admin_order_field = 'object_repr'
    object_repr.short_description = 'Object'

    def action_flag(self, obj):
        return obj.get_action_flag_display()

    action_flag.admin_order_field = 'action_flag'
    action_flag.short_description = 'Action'

    def change_message(self, obj):
        return format_html(obj.change_message)  # 使用format_html来正确展示HTML消息

    change_message.admin_order_field = 'change_message'
    change_message.short_description = 'Change Message'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.index_template = 'custom_admin_template.html'
admin.site.register(UserHistory, UserHistoryAdmin)
admin.site.register(MyUser, MyUserAdmin)
admin.site.register(DownloadRecord, DownloadRecordAdmin)