from .serializers import UserProfileSerializer, EmailVerificationSerializer, ResendEmailVerifySerializer, \
    LoginSerializer, UpdatePasswordSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer, DownloadRecordSerializer
from .models import UserProfile, MyUser, DownloadRecord
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
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes, smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.pagination import PageNumberPagination
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10

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
            data = {
                'url': absurl,
                'toEmail': user.email,
                'emailSubject': 'LTSER 彰化站會員註冊驗證信',
                'username': f'{user.last_name}{user.first_name}'
            }
            Util.send_mail("email_template.html", data)
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
                data = {
                    'url': absurl,
                    'toEmail': user.email,
                    'emailSubject': 'LTSER 彰化站會員註冊驗證信',
                    'username': f'{user.last_name}{user.first_name}'
                }
                Util.send_mail("email_template.html", data)
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

class UserProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        data = request.data
        try:
            userProfile = UserProfile.objects.get(user_id=user.id)
            userProfile.school = data.get('school', userProfile.school)
            userProfile.location = data.get('location', userProfile.location)
            userProfile.department = data.get('department', userProfile.department)
            userProfile.title = data.get('title', userProfile.title)
            userProfile.category = data.get('category', userProfile.category)
            userProfile.application = data.get('application', userProfile.application)
            userProfile.attention = data.get('attention', userProfile.attention)
            userProfile.save()
            return Response({"message": "會員資料更新成功"}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message": "使用者不存在"}, status=status.HTTP_404_NOT_FOUND)
class UpdateUserPasswordAPIView(APIView):
    serializer_class = UpdatePasswordSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            if not user.check_password(request.data['oldPassword']):
                return Response({"message": "舊密碼錯誤"}, status=status.HTTP_400_BAD_REQUEST)

            if request.data['newPassword'] != request.data['newPassword2']:
                return Response({"message": "密碼確認錯誤"}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(request.data['newPassword'])
            user.save()
            data = {
                'toEmail': user.email,
                'emailSubject': 'LTSER 彰化站會員更新密碼',
                'username': f'{user.last_name}{user.first_name}'
            }
            Util.send_mail("password_update_template.html", data)
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': '更新密碼成功'
            }

            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class RequestPasswordResetEmailAPIView(APIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data['email']
        if MyUser.objects.filter(email=email).exists():
            user = MyUser.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            absurl = f'https://www.ltsertwchanghua.org/login/forgot-password/?uidb64={str(uidb64)}&token={str(token)}'
            data = {
                'url': absurl,
                'toEmail': user.email,
                'emailSubject': 'LTSER 彰化站會員重置密碼',
                'username': f'{user.last_name}{user.first_name}'
            }
            Util.send_mail("password_reset_template.html", data)
        return Response({'status': 'success', 'message': '已經寄出連結，請使用連結重置密碼'}, status=status.HTTP_200_OK)

class PasswordTokenCheckAPIView(APIView):
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = MyUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Token is not valid, please request a new one'},
                                status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token},
                            status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Token is not valid, please request a new one'},
                            status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordAPIView(APIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message': '重置密碼成功'}, status=status.HTTP_200_OK)

class DownloadRecordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        paginator = CustomPageNumberPagination()
        records = DownloadRecord.objects.filter(user__id=user.id).order_by('-id')
        result_page = paginator.paginate_queryset(records, request)
        serializer = DownloadRecordSerializer(result_page, many=True)
        return Response({
            'currentPage': paginator.page.number,
            'recordsPerPage': paginator.page_size,
            'totalPages': paginator.page.paginator.num_pages,
            'totalRecords': paginator.page.paginator.count,
            'records': serializer.data
        }, status=status.HTTP_200_OK)