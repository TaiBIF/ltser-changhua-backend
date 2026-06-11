from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
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
    WaterQuality,
    Sediment,
    Crab as DepositarCrab,
    Staff,
    InterviewTag1,
    ResearchesIssue,
    OysterFarmingStats,
    FisheryFarmingStats,
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
    OysterFarmingStatsSerializer,
    FisheryFarmingStatsSerializer,
)
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from datetime import datetime, timedelta
from pathlib import Path
from user.models import DownloadRecord
from django.http import FileResponse
from urllib.parse import parse_qs, urlencode, urlparse
from django.db.models import Q, F
from rest_framework.exceptions import ValidationError
from django.db.models import IntegerField
from django.db.models.functions import Cast
from data.utils.segis_api import *
from django.conf import settings
from data.task import (
    IPT_OBSERVATION_ITEMS,
    import_ckan_and_notify,
    send_import_email,
    send_import_slack,
    sync_ipt_crab_after_success,
)
from data.importing.registry import ADAPTERS, normalize_package_name
from data.utils.email_recipients import get_email_targets
from data.utils.ipt_sync import sync_crab_events, sync_crab_occurrence_extensions
from data.permission import HasInternalApiKey
from celery import chain

import io
import zipfile
import csv
import os
import calendar
import requests
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
    FIELD_MAP = {
        "s_temp": "soilTemperature",
        "t_sal": "tidalPoolSalinity",
        "cw": "soilWater",
        "co": "soilOrganicMatter",
        "s_ph": "soilPH",
        "mm": "medianGrainSize",
        "sc": "sortingCoefficient",
    }

    def get(self, request):
        site = request.query_params.get("site", None)
        if site is not None:
            sediments = Sediment.objects.filter(locationID=site).order_by(
                "eventDate", "id"
            )

            result = []
            for item in sediments:
                data = {
                    "id": item.id,
                    "year": item.eventDate.year,
                    "month": item.eventDate.month,
                    "site": item.locationID,
                    "dataID": item.dataID,
                    "eventDate": item.eventDate,
                }

                for output_field, model_field in self.FIELD_MAP.items():
                    data[output_field] = getattr(item, model_field)

                result.append(data)

            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "No site parameter provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CrabAPIView(APIView):
    def get_species_key(self, scientific_name):
        if not scientific_name:
            return None

        return scientific_name.strip()

    def get(self, request):
        site = request.query_params.get("site", None)
        if site is not None:
            crabs = DepositarCrab.objects.filter(locationID=site).order_by(
                "eventDate", "id"
            )

            grouped = {}
            for crab in crabs:
                key = (crab.eventDate, crab.locationID)
                if key not in grouped:
                    grouped[key] = {
                        "id": crab.id,
                        "year": crab.eventDate.year,
                        "month": crab.eventDate.month,
                        "site": crab.locationID,
                        "species": {},
                        "speciesNames": [],
                        "speciesTitles": {},
                    }

                species_key = self.get_species_key(crab.scientificName)
                if not species_key:
                    continue

                species_title = (
                    crab.vernacularName.strip() if crab.vernacularName else species_key
                )
                grouped[key]["speciesTitles"][species_key] = species_title

                individual_count = crab.individualCount or 0
                grouped[key]["species"][species_key] = (
                    grouped[key]["species"].get(species_key, 0) + individual_count
                )

                if (
                    individual_count > 0
                    and species_title not in grouped[key]["speciesNames"]
                ):
                    grouped[key]["speciesNames"].append(species_title)

            return Response(list(grouped.values()))
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


class WaterQualityAPIView(APIView):
    FIELD_MAP = {
        "w_temp": "waterTemperature",
        "w_ph": "pH",
        "phmv": "hydrogenIon",
        "orp": "oxidationReductionPotential",
        "cond": "conductivity",
        "turb": "turbidity",
        "do": "dissolvedOxygen",
        "tds": "totalDissolvedSolids",
        "w_sal": "salinity",
        "sg": "specificGravity",
    }

    def get(self, request, *args, **kwargs):
        site = request.query_params.get("site", None)
        if site is None:
            return Response(
                {"error": "No site parameter provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        water_quality = WaterQuality.objects.filter(locationID=site).order_by(
            "eventDate", "id"
        )

        result = []
        for item in water_quality:
            data = {"site": item.locationID}
            for output_field, model_field in self.FIELD_MAP.items():
                data[output_field] = getattr(item, model_field)

            result.append(
                {
                    "id": item.id,
                    "dataID": item.dataID,
                    "eventDate": item.eventDate,
                    "year": item.eventDate.year,
                    "month": item.eventDate.month,
                    "data": data,
                }
            )

        return Response(result, status=status.HTTP_200_OK)


class BirdSurveyAPIView(APIView):
    TBIA_OCCURRENCE_API_URL = "https://tbiadata.tw/api/v1/occurrence"

    def get(self, request):
        limit = self.get_limit(request.query_params.get("limit", 20))
        params = {
            "bioGroup": "鳥類",
            "county": "彰化縣",
            "municipality": "芳苑鄉",
            "limit": limit,
        }

        for query_key in ["name", "taxonRank", "eventDate", "cursor"]:
            query_value = request.query_params.get(query_key)
            if query_value:
                params[query_key] = query_value

        try:
            response = requests.get(
                self.TBIA_OCCURRENCE_API_URL,
                params=params,
                timeout=20,
            )
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as exc:
            return Response(
                {"error": f"TBIA API request failed: {str(exc)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except ValueError:
            return Response(
                {"error": "TBIA API returned invalid JSON."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        result["links"] = self.rewrite_links(request, result.get("links", {}))
        return Response(result, status=status.HTTP_200_OK)

    def get_limit(self, raw_limit):
        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            return 20

        return min(max(limit, 1), 1000)

    def rewrite_links(self, request, links):
        rewritten_links = {}
        if links.get("self"):
            rewritten_links["self"] = request.build_absolute_uri()

        next_url = links.get("next")
        if next_url:
            cursor = parse_qs(urlparse(next_url).query).get("cursor", [None])[0]
            if cursor:
                query_params = request.query_params.copy()
                query_params["cursor"] = cursor
                rewritten_links["next"] = request.build_absolute_uri(
                    f"{request.path}?{urlencode(query_params, doseq=True)}"
                )

        return rewritten_links


class BirdSurveyMapAPIView(APIView):
    TBIA_MAP_API_URL = "https://tbiadata.tw/api/v1/map"
    VALID_GRID_LEVELS = {"1", "5", "10", "100"}

    def get(self, request):
        grid = request.query_params.get("grid", "1")
        if grid not in self.VALID_GRID_LEVELS:
            grid = "1"

        params = {
            "boundedBy": request.query_params.get("boundedBy", "121,24,120,23"),
            "grid": grid,
            "bioGroup": "鳥類",
        }

        try:
            response = requests.get(
                self.TBIA_MAP_API_URL,
                params=params,
                timeout=20,
            )
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as exc:
            return Response(
                {"error": f"TBIA map API request failed: {str(exc)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except ValueError:
            return Response(
                {"error": "TBIA map API returned invalid JSON."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(result, status=status.HTTP_200_OK)


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


class DownloadIntertidalTopographyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    INTERTIDAL_FILE_MAP = {
        2002: "Intertidal_Topo_2002_2004.zip",
        2005: "Intertidal_Topo_2005_2007.zip",
        2008: "Intertidal_Topo_2008_2010.zip",
        2011: "Intertidal_Topo_2011_2013.zip",
        2014: "Intertidal_Topo_2014_2015.zip",
        2016: "Intertidal_Topo_2016_2017.zip",
        2018: "Intertidal_Topo_2018.zip",
        2019: "Intertidal_Topo_2019.zip",
        2020: "Intertidal_Topo_2020.zip",
        2021: "Intertidal_Topo_2021.zip",
        2022: "Intertidal_Topo_2022.zip",
        2023: "Intertidal_Topo_2023.zip",
        2024: "Intertidal_Topo_2024.zip",
        2025: "Intertidal_Topo_2025.zip",
    }
    INTERTIDAL_DIR = (
        Path(settings.BASE_DIR).resolve().parent.parent
        / "downloads"
        / "intertidal-topography"
    )

    def get(self, request, *args, **kwargs):
        user = request.user
        year_param = request.query_params.get("year")

        try:
            year = int(year_param)
        except (TypeError, ValueError):
            return Response(
                {"detail": "year 參數格式錯誤"}, status=status.HTTP_400_BAD_REQUEST
            )

        file_name = self.INTERTIDAL_FILE_MAP.get(year)
        if not file_name:
            return Response(
                {"detail": "查無對應年份資料"}, status=status.HTTP_400_BAD_REQUEST
            )
        file_path = self.INTERTIDAL_DIR / file_name
        if not file_path.exists():
            return Response({"detail": "檔案不存在"}, status=status.HTTP_404_NOT_FOUND)

        DownloadRecord.objects.create(
            filename=file_name,
            user=user,
        )

        return FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=file_name,
            content_type="application/zip",
        )


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

    cache_key = f"social_economic_population_data_v3_{scale}"
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

    if scale == "village":
        town_data_sets = [
            get_population_data(
                "town", get_latest_time_list("town", query_type=qt), query_type=qt
            )
            for qt in query_types
        ]
        town_result = convert_population_data(*town_data_sets, "town")

        def is_fangyuan_town_row(item):
            town_id = item.get("鄉鎮市區代碼") or item.get("TOWN_ID")
            town_name = item.get("鄉鎮市區名稱") or item.get("TOWN")
            return str(town_id) == "10007230" or town_name == "芳苑鄉"

        town_by_year = {}
        for year_item in town_result:
            row = next(
                (
                    item
                    for item in year_item.get("data", [])
                    if is_fangyuan_town_row(item)
                ),
                None,
            )
            if row:
                town_by_year[str(year_item.get("year"))] = {
                    **row,
                    "鄉鎮市區代碼": "10007230",
                    "鄉鎮市區名稱": "芳苑鄉",
                    "村里代碼": "10007230-000",
                    "村里名稱": "全芳苑鄉",
                }

        for year_item in result:
            rows = year_item.get("data", [])
            if any(item.get("村里名稱") == "全芳苑鄉" for item in rows):
                continue
            town_row = town_by_year.get(str(year_item.get("year")))
            if town_row:
                rows.append(town_row)

    if len(result) > 0:
        # 將結果用 redis cache 起來，保存期限為 7 天
        cache.set(cache_key, json.dumps(result), timeout=604800)

    return Response(result)


@api_view(["GET"])
def village_pyramid_data(request):
    latest_time = get_latest_time_list("village", query_type="pyramid")
    # 用 latest_map 當作 cache key
    version_str = json.dumps(latest_time, sort_keys=True, ensure_ascii=False)
    version_hash = hashlib.md5(version_str.encode("utf-8")).hexdigest()
    cache_key = f"village_pyramid_data:{version_hash}"

    cached = cache.get(cache_key)
    if cached:
        return Response(cached, status=status.HTTP_200_OK)

    village_population_pyramid = get_population_data(
        "village", latest_time, query_type="pyramid"
    )
    result = covert_pyrimad_data(village_population_pyramid)

    # 寫入快取
    cache.set(cache_key, result, timeout=60 * 60 * 24 * 7)  # 7 天

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

    # 用 latest_map 當作 cache key
    version_str = json.dumps(latest_map, sort_keys=True, ensure_ascii=False)
    version_hash = hashlib.md5(version_str.encode("utf-8")).hexdigest()
    cache_key = f"town_industry_data:v3:{version_hash}"

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


class FangYuanOysterFarmingStatsFormattedView(APIView):
    def get(self, request):
        queryset = OysterFarmingStats.objects.all().order_by("year")
        serializer = OysterFarmingStatsSerializer(queryset, many=True)
        data = serializer.data

        # 轉換成指定格式
        result = []

        # 每年資料
        for row in data:
            result.append(
                {
                    "年份": row.get("year"),
                    "設施（組）": row.get("horizontal_facilities_fangyuan"),
                    "養殖（戶）": row.get("horizontal_farmers_fangyuan"),
                }
            )

        return Response(result)


class OysterFarmingStatsFormattedView(APIView):
    def get(self, request):
        queryset = OysterFarmingStats.objects.all().order_by("year")
        serializer = OysterFarmingStatsSerializer(queryset, many=True)
        data = serializer.data

        nation_result, fangyuan_result, changhua_result = [], [], []

        for row in data:
            # 全國
            nation_result.append(
                {
                    "全國": row.get("year"),
                    "平掛式設施(組)": row.get("horizontal_facilities_nation"),
                    "平掛式養殖（戶）": row.get("horizontal_farmers_nation"),
                    "插篊式設施(組)": row.get("stake_facilities_nation"),
                    "插篊式養殖（戶）": row.get("stake_farmers_nation"),
                    "垂下式設施(棚)": row.get("hanging_facilities_nation"),
                    "垂下式養殖（戶）": row.get("hanging_farmers_nation"),
                    "浮筏式設施(棚)": row.get("raft_facilities_nation"),
                    "浮筏式養殖（戶）": row.get("raft_farmers_nation"),
                    "延繩式設施(組)": row.get("longline_facilities_nation"),
                    "延繩式養殖（戶）": row.get("longline_farmers_nation"),
                    "申報（調查）總戶數": row.get("total_farmers_nation"),
                }
            )

            # 芳苑鄉
            fangyuan_result.append(
                {
                    "芳苑鄉": row.get("year"),
                    "平掛式設施(組)": row.get("horizontal_facilities_fangyuan"),
                    "平掛式養殖（戶）": row.get("horizontal_farmers_fangyuan"),
                    "插篊式設施(組)": row.get("stake_facilities_fangyuan"),
                    "插篊式養殖（戶）": row.get("stake_farmers_fangyuan"),
                    "垂下式設施(棚)": row.get("hanging_facilities_fangyuan"),
                    "垂下式養殖（戶）": row.get("hanging_farmers_fangyuan"),
                    "浮筏式設施(棚)": row.get("raft_facilities_fangyuan"),
                    "浮筏式養殖（戶）": row.get("raft_farmers_fangyuan"),
                    "延繩式設施(組)": row.get("longline_facilities_fangyuan"),
                    "延繩式養殖（戶）": row.get("longline_farmers_fangyuan"),
                    "申報（調查）總戶數": row.get("total_farmers_fangyuan"),
                }
            )

            # 彰化縣
            changhua_result.append(
                {
                    "彰化縣": row.get("year"),
                    "平掛式設施(組)": row.get("horizontal_facilities_changhua"),
                    "平掛式養殖（戶）": row.get("horizontal_farmers_changhua"),
                    "插篊式設施(組)": row.get("stake_facilities_changhua"),
                    "插篊式養殖（戶）": row.get("stake_farmers_changhua"),
                    "垂下式設施(棚)": row.get("hanging_facilities_changhua"),
                    "垂下式養殖（戶）": row.get("hanging_farmers_changhua"),
                    "浮筏式設施(棚)": row.get("raft_facilities_changhua"),
                    "浮筏式養殖（戶）": row.get("raft_farmers_changhua"),
                    "延繩式設施(組)": row.get("longline_facilities_changhua"),
                    "延繩式養殖（戶）": row.get("longline_farmers_changhua"),
                    "申報（調查）總戶數": row.get("total_farmers_changhua"),
                }
            )

        return Response(
            {
                "countryOysterData": nation_result,
                "villageOysterData": fangyuan_result,
                "townOysterData": changhua_result,
            }
        )


class FisheryFarmingStatsFormattedView(APIView):

    # 物種對應名稱
    SPECIES_PREFIX = {
        "文蛤": "hard_clam",
        "烏魚": "mullet",
        "虱目魚": "milkfish",
        "蜆": "asiatic_clam",
        "白蝦": "white_shrimp",
        "吳郭魚": "tilapia",
        "鰻魚": "eel",
        "日本黑蜆": "yamato_clam",
        "西施貝": "purple_clam",
    }

    # 回傳物件名稱
    OUTPUT_KEYS = {
        "文蛤": "villageClamsData",
        "烏魚": "villageMulletData",
        "虱目魚": "villageMilkfishData",
        "蜆": "villageClamData",
        "白蝦": "villageWhiteShrimpData",
        "吳郭魚": "villageTilapiaData",
        "鰻魚": "villageEelData",
        "日本黑蜆": "villageYamatoClamData",
        "西施貝": "villagePurpleClamData",
    }

    # 中英欄位對應
    COL_SUFFIX = {
        "養殖戶數": "households_total",
        "養殖面積（公頃）": "area_hectare",
        "在池-放養量（尾、粒、隻）": "stocking_in_pond",
        "新放養-放養量（尾、粒、隻）": "stocking_new",
        "魚苗戶": "hatchery_households",
        "養殖戶": "farmer_households",
    }

    def build_species_row(self, row: dict, species_label: str, prefix: str) -> dict:
        """把一筆 serializer row 轉成該物種的輸出物件。"""
        out = {species_label: row.get("year")}
        for zh_label, suffix in self.COL_SUFFIX.items():
            out[zh_label] = row.get(f"{prefix}_{suffix}")
        return out

    def get(self, request):
        queryset = FisheryFarmingStats.objects.all().order_by("year")
        serializer = FisheryFarmingStatsSerializer(queryset, many=True)
        data = serializer.data

        result = {out_key: [] for out_key in self.OUTPUT_KEYS.values()}

        for row in data:
            for species_label, prefix in self.SPECIES_PREFIX.items():
                out_key = self.OUTPUT_KEYS[species_label]
                result[out_key].append(
                    self.build_species_row(row, species_label, prefix)
                )

        return Response(result)


class SyncIptCrabEventAPIView(APIView):
    permission_classes = [HasInternalApiKey]

    @staticmethod
    def _to_bool(value, default=False):
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "t", "yes", "y", "on"}

    def post(self, request):
        dry_run = self._to_bool(request.data.get("dry_run"), default=False)
        truncate = self._to_bool(request.data.get("truncate"), default=False)
        limit = request.data.get("limit")

        try:
            result = sync_crab_events(
                dry_run=dry_run,
                truncate=truncate,
                limit=limit,
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)


class SyncIptCrabOccurrenceExtensionAPIView(APIView):
    permission_classes = [HasInternalApiKey]

    @staticmethod
    def _to_bool(value, default=False):
        return SyncIptCrabEventAPIView._to_bool(value, default=default)

    def post(self, request):
        dry_run = self._to_bool(request.data.get("dry_run"), default=False)
        truncate = self._to_bool(request.data.get("truncate"), default=False)
        limit = request.data.get("limit")

        try:
            result = sync_crab_occurrence_extensions(
                dry_run=dry_run,
                truncate=truncate,
                limit=limit,
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(result, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([HasInternalApiKey])
def import_ckan_resource(request):
    base_url = "https://data.depositar.io/zh_Hant_TW"

    resource_id = request.data.get("resource_id")
    site = request.data.get("site")
    observation_item = request.data.get("observation_item")
    resource_name = request.data.get("resource_name")
    base_adapter_id = request.data.get("id")
    limit = request.data.get("limit") or 100

    adapter_id = normalize_package_name(base_adapter_id)

    if not resource_id:
        return Response(
            {"error": "resource_id_required"}, status=status.HTTP_400_BAD_REQUEST
        )

    if not adapter_id:
        return Response({"error": "id_required"}, status=status.HTTP_400_BAD_REQUEST)

    if adapter_id not in ADAPTERS:
        return Response(
            {
                "error": "unknown_dataset",
                "id": adapter_id,
                "allowed": list(ADAPTERS.keys()),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    to_list, cc_list = get_email_targets(observation_item)

    sig1 = import_ckan_and_notify.s(
        package_name=adapter_id,
        resource_id=resource_id,
        base_url=base_url,
        site=site,
        observation_item=observation_item,
        resource_name=resource_name,
        limit=limit,
        notify_slack=False,
    )

    sig_slack = send_import_slack.s(
        site=site,
        observation_item=observation_item,
        resource_name=resource_name,
    )

    # 注意：send_import_email 的第一個參數 report 會自動接到 sig1 的回傳值
    sig2 = send_import_email.s(
        to_emails=to_list,
        cc_emails=cc_list,
        observation_item=observation_item,
        resource_name=resource_name,
        task_id=None,
    )

    if observation_item in IPT_OBSERVATION_ITEMS:
        sig_sync_ipt = sync_ipt_crab_after_success.s(
            observation_item=observation_item,
        )
        result = chain(sig1, sig_sync_ipt, sig_slack, sig2).apply_async()
    else:
        result = chain(sig1, sig_slack, sig2).apply_async()

    return Response(
        {
            "task_id": result.id,  # 這是 chain 的 root id
            "id": adapter_id,
            "resource_id": resource_id,
            "site": site,
            "observation_item": observation_item,
            "resource_name": resource_name,
        },
        status=status.HTTP_202_ACCEPTED,
    )
