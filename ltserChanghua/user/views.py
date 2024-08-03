from .serializers import UserProfileSerializer, EmailVerificationSerializer, ResendEmailVerifySerializer, \
    LoginSerializer, UpdatePasswordSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer, DownloadRecordSerializer, SecurityQuestionSerializer
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
import shutil
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
import csv
import os
import zipfile
from django.apps import apps
from django.http import HttpResponse
from datetime import timedelta
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
            # absurl = f'https://www.ltsertwchanghua.org/mail-verification/?token={str(token)}'
            # data = {
            #     'url': absurl,
            #     'toEmail': user.email,
            #     'emailSubject': 'LTSER 彰化站會員註冊驗證信',
            #     'username': f'{user.last_name}{user.first_name}'
            # }
            # Util.send_mail("email_template.html", data)
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
        user = serializer.validated_data
        user.last_login = timezone.now() + timedelta(hours=8)
        user.save(update_fields=['last_login'])
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            userProfile = UserProfile.objects.get(user_id=user.id)
            serializer = UserProfileSerializer(userProfile)
            data = serializer.data
            data['is_verified'] = user.is_verified
            return Response(data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile does not exist"}, status=status.HTTP_404_NOT_FOUND)


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
            if 'securityQuestion' in data:
                userProfile.securityQuestion = data['securityQuestion']
                userProfile.is_changeSecurityQuestion = True
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
            #Util.send_mail("password_update_template.html", data)
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': '更新密碼成功'
            }

            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ValidateEmailAPIView(APIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = request.data['email']
            if MyUser.objects.filter(email=email).exists():
                return Response({
                    'status': 'success',
                    'message': '此電子郵件已註冊'
                }, status=status.HTTP_200_OK)
            return Response({
                'status': 'error',
                'message': '此電子郵件地址未註冊'
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'status': 'error',
            'message': '無效的數據'
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifySecurityQuestionAPIView(APIView):
    serializer_class = SecurityQuestionSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = request.data['email']
            security_question = request.data['securityQuestion']
            if MyUser.objects.filter(email=email).exists():
                user = MyUser.objects.get(email=email)
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.securityQuestion == security_question:
                    uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                    token = PasswordResetTokenGenerator().make_token(user)
                    absurl = f'https://www.ltsertwchanghua.org/login/forgot-password/?uidb64={str(uidb64)}&token={str(token)}'
                    return Response({
                        'status': 'success',
                        'message': '安全性問題驗證成功',
                        'url': absurl
                    }, status=status.HTTP_200_OK)
                return Response({
                    'status': 'error',
                    'message': '安全性問題錯誤'
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'status': 'error',
                'message': '此電子郵件地址未註冊'
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'status': 'error',
            'message': '無效的數據'
        }, status=status.HTTP_400_BAD_REQUEST)
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




@permission_required('user.can_export_all_models')
def export_all_models(request):
    # 創建臨時目錄來保存 CSV 文件
    temp_dir = 'temp_csv'
    os.makedirs(temp_dir, exist_ok=True)

    # 獲取所有模型
    models = apps.get_models()

    for model in models:
        model_name = model.__name__
        with open(f'{temp_dir}/{model_name}.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # 寫入字段名稱作為表頭
            fields = [field.name for field in model._meta.fields]
            writer.writerow(fields)

            # 寫入每個對象的數據，使用 utf-8 編碼
            for obj in model.objects.all():
                writer.writerow(
                    [str(getattr(obj, field)).encode('utf-8', 'ignore').decode('utf-8') for field in fields])

    # 創建 ZIP 文件
    zip_filename = 'all_models.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                zipf.write(os.path.join(root, file), file)

    # 讀取 ZIP 文件內容並將其作為響應返回
    with open(zip_filename, 'rb') as zipf:
        response = HttpResponse(zipf.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'


    shutil.rmtree(temp_dir)
    os.remove(zip_filename)

    return response
