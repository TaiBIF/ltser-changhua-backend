from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class MyUserManager(BaseUserManager):

    def create_user(self, username, email, password=None, **extra_fields):
        if username is None:
            raise TypeError('創建使用者必須輸入 username')
        if email is None:
            raise TypeError('創建使用者必須輸入 email')

        user = self.model(username=username, email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('創建管理員必須輸入 password')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_verified = True
        user.is_staff = True
        user.is_applied = True
        user.save()
        return user


class MyUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_applied = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = MyUserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save(update_fields=['last_login'])

    class Meta:
        permissions = [
            ("can_export_all_models", "Can export all models"),
        ]
    
    def save(self, *args, **kwargs):
        if not self._state.adding:
            user = MyUser.objects.get(id=self.id)
            if not user.is_verified and self.is_verified:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    self.email.replace('@', 'A'), {
                        'type': 'user_message',
                        'message': f'MyUser model for user {self.username} is verified'
                    }
                )
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    school = models.CharField(max_length=100, null=True, blank=True, editable=True)
    location = models.CharField(max_length=100, null=True, blank=True, editable=True)
    department = models.CharField(max_length=100, null=True, blank=True, editable=True)
    title = models.CharField(max_length=100, null=True, blank=True, editable=True)
    category = models.CharField(max_length=100, null=True, blank=True, editable=True)
    application = models.CharField(max_length=100, null=True, blank=True, editable=True)
    attention = models.CharField(max_length=100, null=True, blank=True, editable=True)
    securityQuestion = models.CharField(max_length=100, null=True, blank=True, editable=True)
    is_changeSecurityQuestion = models.BooleanField(null=True, blank=True, default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class DownloadRecord(models.Model):
    filename = models.CharField(max_length=200)
    time = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='download_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.filename}"

    class Meta:
        db_table = 'DownloadRecord'
        verbose_name = '下載紀錄'
        verbose_name_plural = '下載紀錄'
