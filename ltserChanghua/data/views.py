from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache
from .models import (
    HomepagePhoto,
    LatestEventTag,
    LatestEvent,
    CrabSite,
    WaterQualityManualSite,
    BenthicOrganismData,
    CrabData,
    Literature,
    NewsTag,
    News,
    ResearchTag,
    Research,
    InterviewContent,
    InterviewTag3,
    InterviewTag2,
    InterviewStakeholder,
    InterviewPeople,
    WaterQualityManualData,
    Staff,
    InterviewTag1,
    ResearchesIssue,
)
from .serializers import (
    HomepagePhotoSerializer,
    LatestEventTagSerializer,
    LatestEventSerializer,
    CrabSiteSerializer,
    WaterQualityManualSiteSerializer,
    BenthicOrganismSerializer,
    CrabSerializer,
    LiteratureSerializer,
    NewsTagSerializer,
    NewsSerializer,
    ResearchTagSerializer,
    ResearchSerializer,
    InterviewContentSerializer,
    WaterQualityManualSerializer,
    InterviewTag2Serializer,
    InterviewTag3Serializer,
    StaffSerializer,
    InterviewStakeholderSerializer,
    InterviewTag1Serializer,
    ResearchesIssueSerializer,
)
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
from django.db.models import Q, F
from rest_framework.exceptions import ValidationError
from django.db.models import IntegerField
from django.db.models.functions import Cast
from data.utils.segis_api import *
import hashlib


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
            "currentPage": paginator.page.number,
            "recordsPerPage": paginator.page_size,
            "totalPages": paginator.page.paginator.num_pages,
            "totalRecords": paginator.page.paginator.count,
            "records": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request, pk, format=None):
        latestEvent = LatestEvent.objects.get(id=pk)
        latestEvent.views += 1
        latestEvent.save()
        return Response({"message": "更新觀看數成功"}, status=status.HTTP_200_OK)

    def get_queryset(self, request):
        tag_id = request.GET.get("tag")
        sort_order = request.query_params.get("sort", None)

        if tag_id:
            queryset = LatestEvent.objects.filter(display=True, tags__id=tag_id)
        else:
            queryset = LatestEvent.objects.filter(display=True)

        sort_field = self.SORT_OPTIONS.get(sort_order)
        if sort_field:
            queryset = queryset.order_by(sort_field)
        else:
            queryset = queryset.order_by("-id")

        return queryset


class CrabSiteAPIView(APIView):
    def get(self, request):
        crabSites = CrabSite.objects.all()
        serializer = CrabSiteSerializer(crabSites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WaterQualityManualSiteAPIView(APIView):
    def get(self, request):
        waterQualityManualSites = WaterQualityManualSite.objects.all()
        serializer = WaterQualityManualSiteSerializer(
            waterQualityManualSites, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class BenthicOrganismAPIView(APIView):
    def get(self, request):
        site = request.query_params.get("site", None)
        if site is not None:
            bo = (
                BenthicOrganismData.objects.filter(site=site)
                .annotate(
                    year_int=Cast("year", IntegerField()),
                    month_int=Cast("month", IntegerField()),
                )
                .order_by("year_int", "month_int")
            )

            serializer = BenthicOrganismSerializer(bo, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "No site parameter provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CrabAPIView(APIView):
    def get(self, request):
        site = request.query_params.get("site", None)
        if site is not None:
            crabs = (
                CrabData.objects.filter(site=site)
                .annotate(
                    year_int=Cast("year", IntegerField()),
                    month_int=Cast("month", IntegerField()),
                )
                .order_by("year_int", "month_int")
            )

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
            return Response(
                {"error": "No site parameter provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class WaterQualityManualsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        site = request.query_params.get("site", None)
        wq = WaterQualityManualData.objects.filter(site=site)
        wq = wq.annotate(
            year_int=Cast("year", IntegerField()),
            month_int=Cast("month", IntegerField()),
        ).order_by("year_int", "month_int")
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
        keyword = request.GET.get("keyword")

        if keyword:
            literature = Literature.objects.filter(
                Q(title__icontains=keyword)
            ).order_by("-id")
        else:
            literature = Literature.objects.all().order_by("-id")

        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(literature, request)
        serializer = LiteratureSerializer(result_page, many=True)

        return Response(
            {
                "currentPage": paginator.page.number,
                "recordsPerPage": paginator.page_size,
                "totalPages": paginator.page.paginator.num_pages,
                "totalRecords": paginator.page.paginator.count,
                "records": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

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
        keyword = request.GET.get("keyword")
        tag_id = request.GET.get("tag")

        if keyword:
            news = News.objects.filter(Q(title__icontains=keyword)).order_by("-date")
        elif tag_id:
            news = News.objects.filter(tags__id=tag_id).order_by("-date")
        else:
            # 如果沒有 keyword 和 tag_id，找出離現在最新的兩個月日期
            two_months_ago = datetime.now() - timedelta(days=60)
            news = News.objects.filter(date__gte=two_months_ago).order_by("-date")

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
            "records": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        news = News.objects.get(id=pk)
        news.views += 1
        news.save()
        return Response({"message": "更新新聞觀看數成功"}, status=status.HTTP_200_OK)


class ResearchAPIView(APIView):
    def get(self, request):
        keyword = request.GET.get("keyword")
        tag_id = request.GET.get("tag")

        if keyword:
            research = Research.objects.filter(Q(title__icontains=keyword)).order_by(
                "-year"
            )
        elif tag_id:
            research = Research.objects.filter(tags__id=tag_id).order_by("-year")
        else:
            research = Research.objects.all().order_by("-year")

        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(research, request)
        serializer = ResearchSerializer(result_page, many=True)

        researchTags = ResearchTag.objects.all()
        tag_serializer = ResearchTagSerializer(researchTags, many=True)

        response_data = {
            "currentPage": paginator.page.number,
            "recordsPerPage": paginator.page_size,
            "totalPages": paginator.page.paginator.num_pages,
            "totalRecords": paginator.page.paginator.count,
            "tags": tag_serializer.data,
            "records": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        research = Research.objects.get(id=pk)
        research.views += 1
        research.save()
        return Response(
            {"message": "更新相關研究觀看數成功"}, status=status.HTTP_200_OK
        )


class InterviewSingleAPIView(APIView):

    def get_interview_contents(self, request, update_type="search"):
        d1_str = request.GET.get("d1")
        d2_str = request.GET.get("d2")
        people = request.GET.get("people")
        tag3_values = request.query_params.get("tag3", None)

        if not any([d1_str, d2_str, people, tag3_values]):
            return []

        try:
            if d1_str and d2_str:
                interview_contents = self._filter_by_date(d1_str, d2_str)
            elif people:
                interview_contents = self._filter_by_people(people)
            elif tag3_values:
                tag3_list = (
                    list(map(int, tag3_values.split(","))) if tag3_values else []
                )
                interview_contents = self._filter_by_tag3(tag3_list)
                tag3_instances = InterviewTag3.objects.filter(id__in=tag3_list)
                if update_type == "search":
                    for tag3_instance in tag3_instances:
                        tag3_instance.search_volume += 1
                        tag3_instance.save()
                elif update_type == "download":
                    for tag3_instance in tag3_instances:
                        tag3_instance.download_volume += 1
                        tag3_instance.save()
            else:
                return Response({"error": "No filter provided."}, status=400)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=400)

        return interview_contents

    def get(self, request):
        interview_contents = self.get_interview_contents(request, update_type="search")
        if isinstance(interview_contents, Response):
            return interview_contents

        if not interview_contents:
            return Response({"records": []}, status=status.HTTP_200_OK)

        interview_contents = interview_contents.order_by("-interview_date")

        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(interview_contents, request)

        serializer = InterviewContentSerializer(
            result_page, many=True, context={"request": request}
        )

        response_data = {
            "currentPage": paginator.page.number,
            "recordsPerPage": paginator.page_size,
            "totalPages": paginator.page.paginator.num_pages,
            "totalRecords": paginator.page.paginator.count,
            "records": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    def _filter_by_date(self, d1_str, d2_str):
        d1_year, d1_month = map(int, d1_str.split("-"))
        d2_year, d2_month = map(int, d2_str.split("-"))
        d1_start = datetime(d1_year, d1_month, 1).date()
        last_day_d2 = calendar.monthrange(d2_year, d2_month)[1]
        d2_end = datetime(d2_year, d2_month, last_day_d2).date()
        if d2_end < d1_start:
            raise ValueError("起始時間不能大於結束時間")
        return InterviewContent.objects.filter(interview_date__range=(d1_start, d2_end))

    def _filter_by_people(self, people):
        try:
            person = InterviewPeople.objects.get(title=people)
            return InterviewContent.objects.filter(interview_people=person)
        except InterviewPeople.DoesNotExist:
            raise ValueError("Invalid person ID.")

    def _filter_by_tag3(self, tag3_list):
        try:
            tag3_q = Q(interview_tag3__id__in=tag3_list)
            interview_contents = InterviewContent.objects.filter(tag3_q).distinct()
            return interview_contents
        except ValueError as e:
            raise ValueError(str(e))


class InterviewMultipleAPIView(APIView):
    @staticmethod
    def get_contents_with_scores(request, update_type="search"):
        stakeholder_values = request.query_params.get("stakeholder", None)
        tag2_values = request.query_params.get("tag2", None)
        tag3_values = request.query_params.get("tag3", None)

        # 没有传任何参数
        if not any([stakeholder_values, tag2_values, tag3_values]):
            return []

        if (tag2_values or tag3_values) and not stakeholder_values:
            raise ValidationError({"error": "請傳入受訪對象"})

        if stakeholder_values and not tag2_values and not tag3_values:
            raise ValidationError({"error": "請選擇 1-7 進行搜尋"})

        stakeholder_list = (
            list(map(int, stakeholder_values.split(","))) if stakeholder_values else []
        )
        stakeholder_q = Q(interview_stakeholder__id__in=stakeholder_list)

        matched_contents = InterviewContent.objects.filter(stakeholder_q).distinct()

        if tag2_values or tag3_values:
            tag2_list = list(map(int, tag2_values.split(","))) if tag2_values else []
            tag3_list = list(map(int, tag3_values.split(","))) if tag3_values else []

            if update_type == "search":
                if tag2_list:
                    InterviewTag2.objects.filter(id__in=tag2_list).update(
                        search_volume=F("search_volume") + 1
                    )
                if tag3_list:
                    InterviewTag3.objects.filter(id__in=tag3_list).update(
                        search_volume=F("search_volume") + 1
                    )
            elif update_type == "download":
                if tag2_list:
                    InterviewTag2.objects.filter(id__in=tag2_list).update(
                        download_volume=F("download_volume") + 1
                    )
                if tag3_list:
                    InterviewTag3.objects.filter(id__in=tag3_list).update(
                        download_volume=F("download_volume") + 1
                    )

            tag2_q = Q(interview_tag2__id__in=tag2_list)
            tag3_q = Q(interview_tag3__id__in=tag3_list)

            matched_contents = matched_contents.filter(tag2_q | tag3_q).distinct()

        matched_contents = matched_contents.prefetch_related(
            "interview_tag2", "interview_tag3", "interview_stakeholder"
        )

        def calculate_score(content):
            score = sum(tag2.id in tag2_list for tag2 in content.interview_tag2.all())
            score += sum(tag3.id in tag3_list for tag3 in content.interview_tag3.all())

            return score

        contents_with_scores = [
            (content, calculate_score(content)) for content in matched_contents
        ]

        contents_with_scores.sort(
            key=lambda x: (x[1], x[0].interview_date), reverse=True
        )

        return contents_with_scores

    def get(self, request, *args, **kwargs):
        try:
            contents_with_scores = self.get_contents_with_scores(
                request, update_type="search"
            )
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        paginator = CustomPageNumberPagination()
        result_page = paginator.paginate_queryset(
            [content[0] for content in contents_with_scores], request
        )

        serializer = InterviewContentSerializer(
            result_page, many=True, context={"request": request}
        )

        response_data = {
            "currentPage": paginator.page.number,
            "recordsPerPage": paginator.page_size,
            "totalPages": paginator.page.paginator.num_pages,
            "totalRecords": paginator.page.paginator.count,
            "records": serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class DownloadWaterQualityManyalAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
        except:
            raise PermissionDenied("No permission. Please login as a member.")

        zip_io = io.BytesIO()
        now = datetime.now()
        filename = "LTSER Changhua_水質觀測資料_" + now.strftime("%Y-%m-%d")
        with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zipf:
            csv_file = f"{filename}.csv"
            with open(csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                fields = [
                    field
                    for field in WaterQualityManualData._meta.fields
                    if field.name != "id"
                ]
                writer.writerow([field.name for field in fields])
                for instance in WaterQualityManualData.objects.all().order_by(
                    "year", "month"
                ):
                    row = []
                    for field in fields:
                        value = getattr(instance, field.name)
                        row.append(value)
                    writer.writerow(row)

            zipf.write(csv_file)
            os.remove(csv_file)

        DownloadRecord.objects.create(filename=f"{filename}.csv", user=user)
        zip_io.seek(0)
        response = FileResponse(zip_io, as_attachment=True, filename=f"{filename}.zip")
        return response


class DownloadCrabAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
        except:
            raise PermissionDenied("No permission. Please login as a member.")

        zip_io = io.BytesIO()
        now = datetime.now()
        filename1 = "LTSER Changhua_底質資料_" + now.strftime("%Y-%m-%d")
        filename2 = "LTSER Changhua_螃蟹資料_" + now.strftime("%Y-%m-%d")

        with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zipf:
            for filename, model in [
                (filename1, BenthicOrganismData),
                (filename2, CrabData),
            ]:
                csv_file = f"{filename}.csv"
                with open(csv_file, "w", newline="") as f:
                    writer = csv.writer(f)
                    fields = [
                        field for field in model._meta.fields if field.name != "id"
                    ]
                    writer.writerow([field.name for field in fields])
                    for instance in model.objects.all().order_by("year", "month"):
                        row = []
                        for field in fields:
                            value = getattr(instance, field.name)
                            row.append(value)
                        writer.writerow(row)

                zipf.write(csv_file)
                DownloadRecord.objects.create(filename=f"{filename}.csv", user=user)
                os.remove(csv_file)
        zip_io.seek(0)
        response = FileResponse(
            zip_io,
            as_attachment=True,
            filename=f'LTSER Changhua_底棲生物資料_{now.strftime("%Y-%m-%d")}.zip',
        )
        return response


class InterviewStakeholderListAPIView(APIView):
    def get(self, request):
        interviewstakeholder_list = InterviewStakeholder.objects.all().order_by("order")
        serializer = InterviewStakeholderSerializer(
            interviewstakeholder_list, many=True
        )
        return Response({"records": serializer.data})


class InterviewTag1ListAPIView(APIView):
    def get(self, request):
        interviewtag1_list = InterviewTag1.objects.all().order_by("order")
        serializer = InterviewTag1Serializer(interviewtag1_list, many=True)
        return Response({"records": serializer.data})


class InterviewTag2ListAPIView(APIView):

    @staticmethod
    def extract_option_id(title):
        return title.split(".")[-1][0]

    @staticmethod
    def extract_category_id(title):
        return title.split(".")[0]

    def get(self, request):
        categoryId = request.query_params.get("categoryId", None)

        if categoryId:
            interviewtag2_list = InterviewTag2.objects.filter(
                interview_tag1__title__startswith=str(categoryId)
            ).order_by("order")
        else:
            interviewtag2_list = InterviewTag2.objects.all().order_by("order")
        serializer = InterviewTag2Serializer(interviewtag2_list, many=True)

        # Constructing the response data
        records = []
        for item in serializer.data:
            has_child_tags = InterviewTag3.objects.filter(
                interview_tag2_id=item["id"]
            ).exists()

            option_id_from_title = self.extract_option_id(item["title"])
            category_id_from_title = self.extract_category_id(item["title"])

            optionId = option_id_from_title if not has_child_tags else None
            groupId = option_id_from_title if has_child_tags else None

            data = {
                "tag2": item["id"],
                "categoryId": category_id_from_title,
                "optionId": optionId,
                "groupId": groupId,
                "title": item["title"].split(" ")[-1],
            }
            records.append(data)

        return Response({"records": records})


class InterviewTag3ListAPIView(APIView):

    @staticmethod
    def extract_ids_from_title(title):
        parts = title.split(".")
        categoryId = parts[0] if len(parts) > 0 else None
        groupId = parts[1] if len(parts) > 1 else None
        optionId = parts[2][0] if len(parts) > 2 else None
        return categoryId, groupId, optionId

    def get(self, request):
        categoryId = request.query_params.get("categoryId", None)
        groupId = request.query_params.get("groupId", None)
        if categoryId and groupId:
            tag2_instance = InterviewTag2.objects.filter(
                title__startswith=f"{categoryId}.{groupId} ",
                interview_tag1__title__startswith=str(categoryId),
            ).first()
            if not tag2_instance:
                return Response(
                    {"error": "No matching InterviewTag2 found"}, status=400
                )
            interviewtag3_list = InterviewTag3.objects.filter(
                interview_tag2=tag2_instance
            ).order_by("order")
        else:
            interviewtag3_list = InterviewTag3.objects.all().order_by("order")
        serializer = InterviewTag3Serializer(interviewtag3_list, many=True)

        records = []
        for item in serializer.data:
            catId, grpId, optionId = self.extract_ids_from_title(item["title"])
            data = {
                "tag3": item["id"],
                "categoryId": catId,
                "groupId": grpId,
                "optionId": optionId,
                "title": item["title"].split(" ")[
                    -1
                ],  # Assuming title format remains consistent
            }
            records.append(data)

        return Response({"records": records})


class DownloadInterviewSingleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        if not (user.is_superuser or getattr(user, "is_applied", False)):
            return Response(
                {"detail": "權限不足，請填寫申請表格"}, status=status.HTTP_403_FORBIDDEN
            )

        interview_view = InterviewSingleAPIView()
        interview_contents = interview_view.get_interview_contents(
            request, update_type="download"
        )
        if isinstance(interview_contents, Response):
            return interview_contents

        zip_io = io.BytesIO()
        now = datetime.now()
        filename = "LTSER Changhua_訪談資料_" + now.strftime("%Y-%m-%d")

        with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zipf:
            csv_file_name = f"{filename}.csv"
            csv_io = io.StringIO()

            writer = csv.writer(csv_io)
            # 改变 header
            writer.writerow(["訪談內容", "相關分類", "訪談日期", "受訪者代碼", "類別"])

            # 在 loop 中，按照新的 header 对应地重新排列 row 的内容
            for content in interview_contents:
                row = [
                    content.content,  # 訪談內容
                    " ".join(str(tag) for tag in content.interview_tag2.all())
                    + " "
                    + " ".join(
                        str(tag) for tag in content.interview_tag3.all()
                    ),  # 相關分類
                    content.interview_date,  # 訪談日期
                    " ".join(
                        str(people) for people in content.interview_people.all()
                    ),  # 受訪者代碼
                    " ".join(
                        str(stakeholder)
                        for stakeholder in content.interview_stakeholder.all()
                    ),  # 類別
                ]
                writer.writerow(row)

            csv_io.seek(0)  # reset the stream position to the beginning
            zipf.writestr(
                csv_file_name, csv_io.getvalue()
            )  # write the in-memory text stream to the zip file

        zip_io.seek(0)
        response = FileResponse(zip_io, as_attachment=True, filename=f"{filename}.zip")

        DownloadRecord.objects.create(filename=f"{filename}.csv", user=user)

        return response


class DownloadInterviewMultipleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        if not (user.is_superuser or getattr(user, "is_applied", False)):
            return Response(
                {"detail": "權限不足，請填寫申請表格"}, status=status.HTTP_403_FORBIDDEN
            )

        contents_with_scores = InterviewMultipleAPIView.get_contents_with_scores(
            request, update_type="download"
        )

        zip_io = io.BytesIO()
        now = datetime.now()
        filename = "LTSER Changhua_訪談資料_" + now.strftime("%Y-%m-%d")

        with zipfile.ZipFile(zip_io, "w", zipfile.ZIP_DEFLATED) as zipf:
            csv_file_name = f"{filename}.csv"
            csv_io = io.StringIO()
            writer = csv.writer(csv_io)

            writer.writerow(
                ["id", "類別", "受訪者代碼", "訪談內容", "相關分類", "訪談日期"]
            )
            for content, _ in contents_with_scores:
                tag2_str = "\n".join(str(tag) for tag in content.interview_tag2.all())
                tag3_str = "\n".join(str(tag) for tag in content.interview_tag3.all())
                tags_combined_str = tag2_str
                if tag2_str and tag3_str:
                    tags_combined_str += ",\n" + tag3_str
                elif tag3_str:
                    tags_combined_str = tag3_str

                row = [
                    content.id,
                    " ".join(
                        str(stakeholder)
                        for stakeholder in content.interview_stakeholder.all()
                    ),
                    " ".join(str(people) for people in content.interview_people.all()),
                    content.content,
                    tags_combined_str,
                    content.interview_date,
                ]
                writer.writerow(row)

            csv_io.seek(0)
            zipf.writestr(csv_file_name, csv_io.getvalue())

        zip_io.seek(0)
        response = FileResponse(zip_io, as_attachment=True, filename=f"{filename}.zip")

        # Create a DownloadRecord after successfully creating the zip file.
        DownloadRecord.objects.create(filename=f"{filename}.csv", user=user)

        return response


class StaffAPIView(APIView):
    def get(self, request):
        staff = Staff.objects.all().order_by("order")
        serializer = StaffSerializer(staff, many=True)
        return Response({"records": serializer.data})


class ResearchesIssueAPIView(APIView):
    def get(self, request):
        issue = ResearchesIssue.objects.all().order_by("id").filter(is_display=True)
        serializer = ResearchesIssueSerializer(issue, many=True)
        return Response({"records": serializer.data})


class IncreaseResearchesIssueHitsAPIView(APIView):
    def post(self, request, pk):
        try:
            issue = ResearchesIssue.objects.get(pk=pk)
            issue.hits += 1
            issue.save()
            return Response(
                {"message": "Hits increased", "hits": issue.hits},
                status=status.HTTP_200_OK,
            )
        except ResearchesIssue.DoesNotExist:
            return Response(
                {"error": "Issue not found"}, status=status.HTTP_404_NOT_FOUND
            )


@api_view(["GET"])
def social_economic_population_data(request):
    scale = request.GET.get("scale", "village")

    if scale not in ["village", "town"]:
        return Response(
            {"error": "Invalid scale. Use 'village' or 'town'."}, status=400
        )

    cache_key = f"social_economic_population_data_{scale}"
    cached_data = cache.get(cache_key)

    if cached_data:  # 如果 Redis 中已有資料直接回傳
        return Response(json.loads(cached_data), status=status.HTTP_200_OK)

    query_types = ["index", "summary", "dynamics_index", "structure"]

    # 批次抓取最新資料
    population_data_sets = [
        get_population_data(
            scale, get_latest_time_list(scale, query_type=qt), query_type=qt
        )
        for qt in query_types
    ]

    result = convert_population_data(*population_data_sets, scale)

    if len(result) > 0:
        # 將結果用 redis cache 起來，保存期限為 7 天
        cache.set(cache_key, json.dumps(result), timeout=604800)

    return Response(result)


@api_view(["GET"])
def village_pyramid_data(request):
    latest_time = get_latest_time_list("village", query_type="pyramid")
    village_population_pyramid = get_population_data(
        "village", latest_time, query_type="pyramid"
    )
    result = covert_pyrimad_data(village_population_pyramid)

    return Response(result)


@api_view(["GET"])
def town_industry_data(request):
    query_types = {
        "farming": None,
        "fishing": None,
        "poultry": None,
        "fruit": None,
        "crop": None,
        "special_crop": None,
        "vege": None,
        "rice": None,
        "livestock": None,
        "industry": None,
    }

    try:
        latest_map = {
            qt: get_latest_time_list("town", query_type=qt) for qt in query_types.keys()
        }
    except Exception as e:
        # 若最新時間查詢就失敗，直接回應 500
        return Response({"error": f"get_latest_time_list failed: {str(e)}"}, status=500)

    # 3) 用 latest_map 當作 cache key
    version_str = json.dumps(latest_map, sort_keys=True, ensure_ascii=False)
    version_hash = hashlib.md5(version_str.encode("utf-8")).hexdigest()
    cache_key = f"town_industry_data:{version_hash}"

    cached = cache.get(cache_key)
    if cached:
        return Response(cached, status=status.HTTP_200_OK)

    try:
        data_map = {
            qt: get_industry_data("town", latest_map[qt], query_type=qt)
            for qt in query_types.keys()
        }
    except Exception as e:
        return Response({"error": f"get_industry_data failed: {str(e)}"}, status=500)

    # 組裝各區塊資料
    try:
        industry_map_data = convert_industry_map_data(
            data_map["farming"],
            data_map["fishing"],
            data_map["poultry"],
            data_map["fruit"],
            data_map["crop"],
            data_map["special_crop"],
            data_map["rice"],
            data_map["livestock"],
            data_map["vege"],
            data_map["industry"],
        )

        agriculture_data = convert_agriculture_data(
            data_map["farming"],
            data_map["fruit"],
            data_map["crop"],
            data_map["special_crop"],
            data_map["rice"],
            data_map["vege"],
        )

        industry_and_commerce_data = convert_to_dict_format_data(
            data_map["industry"], INDUSTRY_KEY_MAPPING
        )

        town_fishing_data = convert_to_dict_format_data(
            data_map["fishing"], FISHING_KEY_MAPPING
        )

        town_poultry_data = convert_to_dict_format_data(
            data_map["poultry"], POULTRY_KEY_MAPPING
        )

        town_livestock_data = convert_to_dict_format_data(
            data_map["livestock"], LIVESTOCK_KEY_MAPPING
        )

        result = {
            "townEconomyAndIndustryMapData": industry_map_data,
            "townIndustryAndCommerceData": industry_and_commerce_data,
            "townAgricultureData": agriculture_data,
            "townFisheryData": town_fishing_data,
            "townAnimalHusbandaryPoultryData": town_poultry_data,
            "townAnimalHusbandaryLivestockData": town_livestock_data,
        }
    except Exception as e:
        return Response({"error": f"convert data failed: {str(e)}"}, status=500)

    # 寫入快取
    cache.set(cache_key, result, timeout=60 * 60 * 24 * 7)  # 7 天

    return Response(result, status=status.HTTP_200_OK)
