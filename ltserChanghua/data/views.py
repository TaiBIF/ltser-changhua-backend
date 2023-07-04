from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HomepagePhoto
from .serializers import HomepagePhotoSerializer
from rest_framework import status
class HomepagePhotoAPIView(APIView):
    def get(self, request):
        homepagePhotos = HomepagePhoto.objects.filter(display=True)
        serializer = HomepagePhotoSerializer(homepagePhotos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
