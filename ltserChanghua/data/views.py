from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HomepagePhoto, LatestEventTag, LatestEvent, CrabSite, WaterQualityManualSite, BenthicOrganism, \
    Crab, \
    WaterQualityManual, Literature, NewsTag, News, ResearchTag, Research
from .serializers import HomepagePhotoSerializer, LatestEventTagSerializer, LatestEventSerializer, CrabSiteSerializer, \
    WaterQualityManualSiteSerializer, BenthicOrganismSerializer, CrabSerializer, WaterQualityManualSerializer, \
    LiteratureSerializer, NewsTagSerializer, NewsSerializer, ResearchTagSerializer, ResearchSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta

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
    SORT_OPTIONS = {
        "dateAscending": "activityTime",
        "dateDescending": "-activityTime",
        "views": "-views",
    }

    def get(self, request):
        queryset = self.get_queryset(request)

        # Add pagination
        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LatestEventSerializer(result_page, many=True)

        response_data = {
            'currentPage': paginator.page.number,
            'recordsPerPage': paginator.page_size,
            'totalPages': paginator.page.paginator.num_pages,
            'totalRecords': paginator.page.paginator.count,
            'records': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request, pk, format=None):
        latestEvent = LatestEvent.objects.get(id=pk)
        latestEvent.views += 1
        latestEvent.save()
        return Response({"message": "更新觀看數成功"}, status=status.HTTP_200_OK)

    def get_queryset(self, request):
        tag_id = request.GET.get('tag')
        sort_order = request.query_params.get('sort', None)

        if tag_id:
            queryset = LatestEvent.objects.filter(display=True, tags__id=tag_id)
        else:
            queryset = LatestEvent.objects.filter(display=True)

        sort_field = self.SORT_OPTIONS.get(sort_order)
        if sort_field:
            queryset = queryset.order_by(sort_field)
        else:
            queryset = queryset.order_by('-id')

        return queryset



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

class NewsTagsAPIView(APIView):
    def get(self, request):
        newstags = NewsTag.objects.all()
        serializer = NewsTagSerializer(newstags, many=True)
        return Response(serializer.data)


class NewsAPIView(APIView):
    def get(self, request):
        tag_id = request.GET.get('tag')
        if tag_id:
            # 如果有 tag_id，則根據日期順序排序
            news = News.objects.filter(tags__id=tag_id).order_by('-date')
        else:
            # 如果沒有 tag_id，找出離現在最新的兩個月日期
            two_months_ago = datetime.now() - timedelta(days=60)
            news = News.objects.filter(date__gte=two_months_ago).order_by('-date')

        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(news, request)
        serializer = NewsSerializer(result_page, many=True)

        # 獲取所有新聞標籤
        newstags = NewsTag.objects.all()
        tag_serializer = NewsTagSerializer(newstags, many=True)

        # 將數據整理成所需的回傳格式
        response_data = {
            "currentPage": paginator.page.number,
            "recordsPerPage": paginator.page_size,
            "totalPages": paginator.page.paginator.num_pages,
            "totalRecords": paginator.page.paginator.count,
            "tags": tag_serializer.data,
            "records": serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        news = News.objects.get(id=pk)
        news.views += 1
        news.save()
        return Response({"message": "更新新聞觀看數成功"}, status=status.HTTP_200_OK)

class ResearchAPIView(APIView):
    def get(self, request):
        tag_id = request.GET.get('tag')
        if tag_id:
            # 如果有 tag_id，則根據日期順序排序
            research = Research.objects.filter(tags__id=tag_id).order_by('-year')
        else:
            research =  Research.objects.all().order_by('-year')

        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(research, request)
        serializer = ResearchSerializer(result_page, many=True)

        researchTags = ResearchTag.objects.all()
        tag_serializer = ResearchTagSerializer(researchTags, many=True)

        # 將數據整理成所需的回傳格式
        response_data = {
            "currentPage": paginator.page.number,
            "recordsPerPage": paginator.page_size,
            "totalPages": paginator.page.paginator.num_pages,
            "totalRecords": paginator.page.paginator.count,
            "tags": tag_serializer.data,
            "records": serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        research = Research.objects.get(id=pk)
        research.views += 1
        research.save()
        return Response({"message": "更新相關研究觀看數成功"}, status=status.HTTP_200_OK)