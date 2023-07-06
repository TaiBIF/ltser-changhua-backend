from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import UserProfile, MyUser
from django.core.validators import RegexValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=MyUser.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True,
                                     validators=[RegexValidator(regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d\!\@\#\$\%\^\&\*\(\)\-\_\+\=\{\}\[\]\:\;\.\,]{8,}$'
,message="密碼長度至少8位，並且包含至少一個英文字母和一個數字")])
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

class UserProfileSerializer(serializers.ModelSerializer):
    user = RegisterSerializer(required=True, many=False)
    school = serializers.CharField(required=True)
    location = serializers.CharField(required=True)
    department = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    category = serializers.CharField(required=True)

    class Meta:
        model = UserProfile
        fields = "__all__"

    def create(self, validated_data):
        userData = validated_data.pop('user')
        user = RegisterSerializer.create(RegisterSerializer(), validated_data=userData)
        userProfile = UserProfile.objects.create(user=user, **validated_data)
        return userProfile

class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=1000)

    class Meta:
        model = MyUser
        fields = ['token']


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

        if not user.is_active:
            raise AuthenticationFailed('尚未確認驗證信')

        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        token = self.get_token(instance)
        return token
