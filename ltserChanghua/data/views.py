from rest_framework.views import APIView
from rest_framework.response import Response
from .models import HomepagePhoto, LatestEventTag, LatestEvent, CrabSite, WaterQualityManualSite, BenthicOrganism, \
    Crab, \
    WaterQualityManual, Literature, NewsTag, News, ResearchTag, Research, InterviewContent, InterviewTag3, \
    InterviewTag2, InterviewStakeholder, InterviewPeople
from .serializers import HomepagePhotoSerializer, LatestEventTagSerializer, LatestEventSerializer, CrabSiteSerializer, \
    WaterQualityManualSiteSerializer, BenthicOrganismSerializer, CrabSerializer, WaterQualityManualSerializer, \
    LiteratureSerializer, NewsTagSerializer, NewsSerializer, ResearchTagSerializer, ResearchSerializer, InterviewContentSerializer
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
import io
from datetime import datetime, timedelta
import zipfile
import csv
import os
from user.models import DownloadRecord
from django.http import FileResponse
import calendar
from django.db.models import Q

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

class InterviewSingleAPIView(APIView):
    def get(self, request):
        d1_str = request.GET.get('d1')
        d2_str = request.GET.get('d2')
        people = request.GET.get('people')

        # 轉換 d1 和 d2 為日期範圍
        d1_year, d1_month = map(int, d1_str.split('-'))
        d2_year, d2_month = map(int, d2_str.split('-'))

        # 獲取 d1 的開始日期 (第一天)
        d1_start = datetime(d1_year, d1_month, 1).date()

        # 獲取 d2 的結束日期 (該月的最後一天)
        last_day_d2 = calendar.monthrange(d2_year, d2_month)[1]
        d2_end = datetime(d2_year, d2_month, last_day_d2).date()

        try:
            person = InterviewPeople.objects.get(title=people)
            interview_contents = InterviewContent.objects.filter(interview_date__range=(d1_start, d2_end), interview_people=person).order_by('-interview_date')
        except InterviewPeople.DoesNotExist:
            return Response({"error": "Invalid person ID."}, status=400)

        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(interview_contents, request)

        serializer = InterviewContentSerializer(result_page, many=True, context={'request': request})

        response_data = {
            "currentPage": paginator.page.number,
            "recordsPerPage": paginator.page_size,
            "totalPages": paginator.page.paginator.num_pages,
            "totalRecords": paginator.page.paginator.count,
            "records": serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

class InterviewMultipleAPIView(APIView):
    def get(self, request):
        tag2_values = request.query_params.get('tag2', None)
        tag3_values = request.query_params.get('tag3', None)
        stakeholder_values = request.query_params.get('stakeholder', None)

        query = Q()

        # Check and filter by tag2 values
        if tag2_values:
            tag2_list = [int(tag) for tag in tag2_values.split(',')]
            query |= Q(interview_tag2__id__in=tag2_list)

        # Check and filter by tag3 values
        if tag3_values:
            tag3_list = [int(tag) for tag in tag3_values.split(',')]
            query |= Q(interview_tag3__id__in=tag3_list)

        # Check and filter by stakeholder values
        if stakeholder_values:
            stakeholder_list = [int(stakeholder) for stakeholder in stakeholder_values.split(',')]
            query |= Q(interview_stakeholder__id__in=stakeholder_list)


        interview_contents = InterviewContent.objects.filter(query).order_by('-interview_date')


        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(interview_contents, request)
        serializer = InterviewContentSerializer(result_page, many=True, context={'request': request})
        return Response(serializer.data)

class DownloadWaterQualityManyalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
        except:
            raise PermissionDenied('No permission. Please login as a member.')

        zip_io = io.BytesIO()
        now = datetime.now()
        filename = "LTSER Changhua_水質觀測資料_" + now.strftime("%Y-%m-%d")
        with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
            csv_file = f'{filename}.csv'
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([field.name for field in WaterQualityManual._meta.fields])
                for instance in WaterQualityManual.objects.all():
                    row = []
                    for field in WaterQualityManual._meta.fields:
                        value = getattr(instance, field.name)
                        row.append(value)
                    writer.writerow(row)

            zipf.write(csv_file)
            os.remove(csv_file)

        DownloadRecord.objects.create(filename=f'{filename}.csv', user=user)
        zip_io.seek(0)
        response = FileResponse(zip_io, as_attachment=True, filename=f'{filename}.zip')
        return response


class DownloadCrabAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
        except:
            raise PermissionDenied('No permission. Please login as a member.')

        zip_io = io.BytesIO()
        now = datetime.now()
        filename1 = "LTSER Changhua_底質資料" + now.strftime("%Y-%m-%d")
        filename2 = "LTSER Changhua_螃蟹資料" + now.strftime("%Y-%m-%d")

        with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, model in [(filename1, BenthicOrganism), (filename2, Crab)]:
                csv_file = f'{filename}.csv'
                with open(csv_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([field.name for field in model._meta.fields])
                    for instance in model.objects.all():
                        row = []
                        for field in model._meta.fields:
                            value = getattr(instance, field.name)
                            row.append(value)
                        writer.writerow(row)

                zipf.write(csv_file)
                DownloadRecord.objects.create(filename=f'{filename}.csv', user=user)
                os.remove(csv_file)
        zip_io.seek(0)
        response = FileResponse(zip_io, as_attachment=True, filename=f'LTSER Changhua_底棲生物資料_{now.strftime("%Y-%m-%d")}.zip')
        return response