from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HomepagePhoto, LatestEventTag, LatestEvent, CrabSite, WaterQualityManualSite, BenthicOrganism, \
    Crab, \
    WaterQualityManual, Literature
from .serializers import HomepagePhotoSerializer, LatestEventTagSerializer, LatestEventSerializer, CrabSiteSerializer, \
    WaterQualityManualSiteSerializer, BenthicOrganismSerializer, CrabSerializer, WaterQualityManualSerializer, LiteratureSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10

class HomepagePhotoAPIView(APIView):
    def get(self, request):
        homepagePhotos = HomepagePhoto.objects.filter(display=True)
        serializer = HomepagePhotoSerializer(homepagePhotos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class LatestEventTagAPIView(APIView):
    def get(self, request):
        tags = LatestEventTag.objects.all()
        serializer = LatestEventTagSerializer(tags, many=True)
        return Response(serializer.data)


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


class CrabSiteAPIView(APIView):
    def get(self, request):
        crabSites = CrabSite.objects.all()
        serializer = CrabSiteSerializer(crabSites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class WaterQualityManualSiteAPIView(APIView):
    def get(self, request):
        waterQualityManualSites = WaterQualityManualSite.objects.all()
        serializer = WaterQualityManualSiteSerializer(waterQualityManualSites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BenthicOrganismAPIView(APIView):
    def get(self, request):
        site = request.query_params.get('site', None)
        if site is not None:
            bo = BenthicOrganism.objects.filter(site=site)
            serializer = BenthicOrganismSerializer(bo, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No site parameter provided."}, status=status.HTTP_200_OK)

class CrabAPIView(APIView):
    def get(self, request):
        site = request.query_params.get('site', None)
        if site is not None:
            crabs = Crab.objects.filter(site=site)
            serializer = CrabSerializer(crabs, many=True)
            list_of_objects = serializer.data
            res = []
            for dic in list_of_objects:
                obj = {}
                species = {}
                for key, value in dic.items():
                    if key in ["id", "year", "site", "month"]:
                        obj[key] = value
                    else:
                        species[key] = value
                obj["species"] = species
                res.append(obj)
            return Response(res)
        else:
            return Response({"error": "No site parameter provided."}, status=status.HTTP_400_BAD_REQUEST)

class WaterQualityManualsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        site = request.query_params.get('site', None)
        wq = WaterQualityManual.objects.filter(site=site)
        serializer = WaterQualityManualSerializer(wq, many=True)
        list_of_objects = serializer.data
        res = []
        for dic in list_of_objects:
            obj = {}
            data = {}
            for key, value in dic.items():
                if key == "id" or key == "year" or key == "month":
                    obj[key] = value
                else:
                    data[key] = value
            obj["data"] = data
            res.append(obj)
        return Response(res, status=status.HTTP_200_OK)

class LiteratureAPIView(APIView):
    def get(self, request):
        paginator = CustomPageNumberPagination()
        literature = Literature.objects.all().order_by('-id')
        result_page = paginator.paginate_queryset(literature, request)
        serializer = LiteratureSerializer(result_page, many=True)
        return Response({
            'currentPage': paginator.page.number,
            'recordsPerPage': paginator.page_size,
            'totalPages': paginator.page.paginator.num_pages,
            'totalRecords': paginator.page.paginator.count,
            'records': serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        literature = Literature.objects.get(id=pk)
        literature.views += 1
        literature.save()
        return Response({"message": "更新文獻觀看數成功"}, status=status.HTTP_200_OK)