from .serializers import UserProfileSerializer, EmailVerificationSerializer, ResendEmailVerifySerializer, LoginSerializer
from .models import UserProfile, MyUser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .utils import Util
import jwt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
class RegisterAPIView(APIView):
    serializer_class = UserProfileSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            userData = serializer.data
            user = MyUser.objects.get(email=userData['user']['email'])
            token = RefreshToken.for_user(user).access_token
            absurl = f'https://www.ltsertwchanghua.org/mail-verification/?token={str(token)}'
            emailBody = f'Hi {user.last_name}{user.first_name} 請點擊以下連結驗證會員註冊：\n {absurl}'
            data = {'emailBody': emailBody, 'toEmail': user.email, 'emailSubject': '長期社會生態核心觀測彰化站註冊會員驗證信'}
            Util.send_mail(data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailAPIView(APIView):
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        token = request.GET.get('token')
        try:
            payload =jwt.decode(str(token), settings.SECRET_KEY, 'HS256')
            user = MyUser.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class ResendEmailVerifyAPIView(APIView):
    serializer_class = ResendEmailVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = MyUser.objects.get(email=email)
            if user.is_verified:
                return Response({"message": "使用者已被激活"}, status=status.HTTP_409_CONFLICT)
            else:
                token = RefreshToken.for_user(user).access_token
                absurl = f'https://www.ltsertwchanghua.org/mail-verification/?token={str(token)}'
                emailBody = f'Hi {user.last_name}{user.first_name} 請點擊以下連結驗證會員註冊：\n {absurl}'
                data = {'emailBody': emailBody, 'toEmail': user.email, 'emailSubject': '長期社會生態核心觀測彰化站註冊會員驗證信'}
                Util.send_mail(data)
                return Response({"message": "已重新發送驗證信"}, status= status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "使用者不存在"}, status=status.HTTP_404_NOT_FOUND)

class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        userProfile = UserProfile.objects.get(user_id=user.id)
        serializer = UserProfileSerializer(userProfile)
        return Response(serializer.data, status=status.HTTP_200_OK)