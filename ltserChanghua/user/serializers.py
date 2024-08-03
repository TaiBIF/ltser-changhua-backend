from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import UserProfile, MyUser, DownloadRecord
from django.core.validators import RegexValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils import timezone


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=MyUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True,
                                     validators=[RegexValidator(
                                         regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d\!\@\#\$\%\^\&\*\(\)\-\_\+\=\{\}\['
                                               r'\]\:\;\.\,]{8,}$'
                                         , message="密碼長度至少8位，並且包含至少一個英文字母和一個數字")])
    password2 = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = MyUser
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = MyUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=1000)

    class Meta:
        model = MyUser
        fields = ['token']


class ResendEmailVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        # 檢查郵件是否存在於 User 模型中
        if not MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('提供的郵件地址不存在。')

        return attrs


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=255, min_length=8, write_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = MyUser
        fields = ['username', 'password', 'token']

    @staticmethod
    def get_token(obj):
        refresh = RefreshToken.for_user(obj)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']
        user = authenticate(username=username, password=password)

        if not user:
            raise AuthenticationFailed('無效的帳號或密碼')

        # if not user.is_verified:
        #     raise AuthenticationFailed('尚未確認驗證信')

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        token = self.get_token(instance)
        return token


class UserProfileSerializer(serializers.ModelSerializer):
    user = RegisterSerializer(required=True, many=False)
    school = serializers.CharField(required=True)
    location = serializers.CharField(required=True)
    department = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    category = serializers.CharField(required=True)
    securityQuestion = serializers.CharField(required=True)
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"

    def create(self, validated_data):
        userData = validated_data.pop('user')
        user = RegisterSerializer.create(RegisterSerializer(), validated_data=userData)
        userProfile = UserProfile.objects.create(user=user, **validated_data)
        return userProfile

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = instance.user
        user_data = {
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        if not user.is_verified:
            return {
                "user": user_data,
                "is_verified": False
            }
        representation["user"] = user_data
        representation["is_verified"] = True
        representation.pop('is_changeSecurityQuestion', None)
        if instance.is_changeSecurityQuestion:
            representation.pop('securityQuestion', None)
        return representation

class UpdatePasswordSerializer(serializers.ModelSerializer):
    newPassword = serializers.CharField(write_only=True, required=True)
    newPassword2 = serializers.CharField(write_only=True, required=True)
    oldPassword = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = MyUser
        fields = ('newPassword', 'newPassword2', 'oldPassword')


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        model = MyUser
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = MyUser.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise AuthenticationFailed('The rest link is invalid', 401)


class DownloadRecordSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()

    class Meta:
        model = DownloadRecord
        fields = ['filename', 'time']

    def get_time(self, obj):
        return (obj.time + timezone.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')


class SecurityQuestionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    securityQuestion = serializers.CharField(max_length=100)
