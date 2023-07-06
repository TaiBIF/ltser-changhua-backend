from django.shortcuts import render
from .serializers import UserProfileSerializer
from .models import UserProfile, MyUser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.response import Response
from .utils import Util
class RegisterAPIView(APIView):
    serializer_class = UserProfileSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            userData = serializer.data
            user = MyUser.objects.get(email=userData['user']['email'])
            token = RefreshToken.for_user(user).access_token
            #current_site = get_current_site(request).domain
            #relativeLink = reverse('email-verify')
            absurl = f'https://www.ltsertwchanghua.org/mail-verification/?token={str(token)}'
            emailBody = f'Hi {user.last_name}{user.first_name} 請點擊以下連結驗證會員註冊：\n {absurl}'
            data = {'emailBody': emailBody, 'toEmail': user.email, 'emailSubject': '長期社會生態核心觀測彰化站註冊會員驗證信'}
            Util.send_mail(data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
