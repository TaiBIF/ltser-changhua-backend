from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HomepagePhoto, LatestEvent
from .serializers import HomepagePhotoSerializer, LatestEventSerializer
from rest_framework import status
class HomepagePhotoAPIView(APIView):
    def get(self, request):
        homepagePhotos = HomepagePhoto.objects.filter(display=True)
        serializer = HomepagePhotoSerializer(homepagePhotos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LatestEventAPIView(APIView):
    def get(self, request):
        queryset = LatestEvent.objects.filter(display=True)
        sort_order = request.query_params.get('sort', None)
        if sort_order == "dateAscending":
            queryset = queryset.order_by("activityTime")
        elif sort_order == 'dateDescending':
            queryset = queryset.order_by("-activityTime")
        elif sort_order == 'views':
            queryset = queryset.order_by("-views")

        serializer = LatestEventSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChangeLatestEventViewsAPIView(APIView):

    def patch(self, request, pk, format=None):
        latestEvent = LatestEvent.objects.get(id=pk)
        latestEvent.views += 1
        latestEvent.save()
        return Response({"message": "更新觀看數成功"},status=status.HTTP_200_OK)