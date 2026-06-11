import re

import requests

from django.db import connection, transaction

from data.models import Crab, IptCrabEvent, IptCrabOccurrenceExtension

DEFAULT_COUNTRY = "Taiwan"
DEFAULT_COUNTRY_CODE = "TW"
DEFAULT_COUNTY = "Changhua County"
DEFAULT_MUNICIPALITY = "Fangyuan Township"
DEFAULT_PROTOCOL = "Quantitative sampling (1 m2 quadrat)"
DEFAULT_SAMPLE_SIZE_VALUE = 3
DEFAULT_SAMPLE_SIZE_UNIT = "square meters"
DEFAULT_SAMPLING_EFFORT = (
    "Estimated three times, using the maximum value as the result for each quadrat"
)
DEFAULT_KINGDOM = "Animalia"
NOMENMATCH_URL = "https://match.taibif.tw/v2/api.php"
NOMENMATCH_CHUNK_SIZE = 20
NOMENMATCH_TIMEOUT = 30


def build_event_id(row):
    event_id = row_value(row, "eventID")
    event_date = row_value(row, "eventDate")
    if event_id:
        return event_id
    if row.locationID and event_date:
        return f"CRAB-{row.locationID}-{event_date.strftime('%Y%m%d')}"
    if event_date:
        return f"CRAB-{event_date.strftime('%Y%m%d')}-{row.pk}"
    return f"CRAB-{row.pk}"


def event_date_str(value):
    if value:
        return value.strftime("%Y-%m-%d")
    return ""


def to_sampling_protocol_en(sampling_protocol):
    return DEFAULT_PROTOCOL


def row_class_value(row):
    return getattr(row, "class_field", None) or getattr(row, "class_name", None)


def row_value(row, field_name):
    return getattr(row, field_name, None)


def normalize_taxon_name(value):
    if not value:
        return ""
    normalized = str(value).strip()
    normalized = re.sub(r"(?i)(^|\s)spp?\.?(?=\s|$)", " ", normalized)
    return " ".join(normalized.split())


def lowercase_taxon_rank(value):
    if not value:
        return None
    return str(value).strip().lower()


def chunked(values, size):
    for index in range(0, len(values), size):
        yield values[index : index + size]


def iter_taibif_match_items(value):
    if isinstance(value, dict):
        if "results" in value:
            yield value
        return

    if isinstance(value, list):
        for item in value:
            yield from iter_taibif_match_items(item)


def taxon_payload_from_result(result):
    accepted_namecode = result.get("accepted_namecode")
    parent_name_usage_id = None
    if accepted_namecode:
        parent_name_usage_id = f"{accepted_namecode}(TaiCOL)"

    return {
        "kingdom": result.get("kingdom") or DEFAULT_KINGDOM,
        "phylum": result.get("phylum"),
        "class_field": result.get("class"),
        "order": result.get("order"),
        "family": result.get("family"),
        "genus": result.get("genus"),
        "taxonRank": result.get("taxon_rank"),
        "acceptedNameUsageID": parent_name_usage_id,
    }


def select_nomenmatch_result(results):
    for result in results:
        if str(result.get("kingdom") or "").strip().lower() == "animalia":
            return result
    return results[0]


def fetch_nomenmatch_taxon_map(scientific_names):
    taxon_map = {}
    errors = []
    names = sorted({normalize_taxon_name(name) for name in scientific_names if name})

    for names_chunk in chunked(names, NOMENMATCH_CHUNK_SIZE):
        try:
            response = requests.get(
                NOMENMATCH_URL,
                params={
                    "format": "json",
                    "best": "yes",
                    "source": "taicol",
                    "names": "|".join(names_chunk),
                },
                timeout=NOMENMATCH_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            errors.append({"names": names_chunk, "error": str(exc)})
            continue
        except ValueError as exc:
            errors.append({"names": names_chunk, "error": f"invalid_json: {exc}"})
            continue

        for item in iter_taibif_match_items(payload.get("data")):
            results = item.get("results") or []
            if not results:
                continue

            result = select_nomenmatch_result(results)
            taxon_payload = taxon_payload_from_result(result)
            for key in (
                item.get("search_term"),
                item.get("name_cleaned"),
                item.get("matched_clean"),
                result.get("simple_name"),
            ):
                normalized = normalize_taxon_name(key)
                if normalized:
                    taxon_map[normalized] = taxon_payload

    return taxon_map, errors


def validate_limit(limit):
    if limit is None:
        return None

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        raise ValueError("limit must be an integer")

    if limit <= 0:
        raise ValueError("limit must be > 0")

    return limit


def crab_queryset(limit=None):
    limit = validate_limit(limit)
    queryset = Crab.objects.all().order_by("id")
    if limit is not None:
        return queryset[:limit]
    return queryset


def check_scientific_names(limit=None):
    limit = validate_limit(limit)
    names = set()
    queryset = Crab.objects.exclude(scientificName__isnull=True).exclude(
        scientificName=""
    )

    if limit is None:
        values = (
            queryset.order_by("scientificName")
            .values_list("scientificName", flat=True)
            .distinct()
        )
    else:
        values = queryset.order_by("id").values_list("scientificName", flat=True)[
            :limit
        ]

    for name in values:
        normalized = normalize_taxon_name(name)
        if normalized:
            names.add(normalized)

    return names


def sync_crab_events(dry_run=False, truncate=False, limit=None):
    queryset = crab_queryset(limit=limit)

    grouped_events = {}
    for row in queryset:
        event_id = build_event_id(row)
        if event_id not in grouped_events:
            grouped_events[event_id] = {
                "eventDate": event_date_str(row.eventDate),
                "samplingProtocol": to_sampling_protocol_en(row.samplingProtocol),
                "sampleSizeValue": DEFAULT_SAMPLE_SIZE_VALUE,
                "sampleSizeUnit": DEFAULT_SAMPLE_SIZE_UNIT,
                "samplingEffort": DEFAULT_SAMPLING_EFFORT,
                "locationID": row.locationID,
                "country": DEFAULT_COUNTRY,
                "countryCode": DEFAULT_COUNTRY_CODE,
                "county": DEFAULT_COUNTY,
                "municipality": DEFAULT_MUNICIPALITY,
                "locality": row.locationID,
                "verbatimLocality": row.locality,
                "decimalLatitude": row.decimalLatitude,
                "decimalLongitude": row.decimalLongitude,
                "geodeticDatum": row.geodeticDatum,
            }

        group = grouped_events[event_id]
        if row.samplingProtocol and group["samplingProtocol"] == DEFAULT_PROTOCOL:
            group["samplingProtocol"] = to_sampling_protocol_en(row.samplingProtocol)
        if row.locality and not group["verbatimLocality"]:
            group["verbatimLocality"] = row.locality
        if row.locationID and not group["locationID"]:
            group["locationID"] = row.locationID
        if not group["eventDate"] and row.eventDate:
            group["eventDate"] = event_date_str(row.eventDate)

    payloads = []
    skipped_no_event_date = 0
    for event_id, payload in grouped_events.items():
        if not payload["eventDate"]:
            skipped_no_event_date += 1
            continue
        payloads.append((event_id, payload))

    existing_ids = set()
    if not truncate:
        existing_ids = set(IptCrabEvent.objects.values_list("eventID", flat=True))

    created_count = 0
    updated_count = 0

    if dry_run:
        for event_id, _payload in payloads:
            if event_id in existing_ids:
                updated_count += 1
            else:
                created_count += 1
    else:
        with transaction.atomic():
            if truncate:
                table_name = IptCrabEvent._meta.db_table
                with connection.cursor() as cursor:
                    cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY;')

            for event_id, payload in payloads:
                _, created = IptCrabEvent.objects.update_or_create(
                    eventID=event_id,
                    defaults=payload.copy(),
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

    return {
        "dry_run": dry_run,
        "truncate": truncate,
        "source_records": queryset.count(),
        "grouped_events": len(grouped_events),
        "synced_events": len(payloads),
        "skipped_no_event_date": skipped_no_event_date,
        "created": created_count,
        "updated": updated_count,
    }


def sync_crab_occurrence_extensions(dry_run=False, truncate=False, limit=None):
    queryset = crab_queryset(limit=limit)
    requested_taxon_names = check_scientific_names(limit=limit)
    taxon_map, taxon_lookup_errors = fetch_nomenmatch_taxon_map(requested_taxon_names)

    occurrence_payloads = {}
    skipped_no_occurrence_id = 0
    skipped_no_scientific_name = 0

    for row in queryset:
        if not row.dataID:
            skipped_no_occurrence_id += 1
            continue
        if not row.scientificName:
            skipped_no_scientific_name += 1
            continue

        taxon = taxon_map.get(normalize_taxon_name(row.scientificName)) or {}
        occurrence_payloads[row.dataID] = {
            "eventID": build_event_id(row),
            "basisOfRecord": row.basisOfRecord,
            "scientificName": row.scientificName,
            "individualCount": row.individualCount,
            "eventDate": event_date_str(row.eventDate),
            "decimalLatitude": row.decimalLatitude,
            "decimalLongitude": row.decimalLongitude,
            "kingdom": taxon.get("kingdom") or DEFAULT_KINGDOM,
            "phylum": taxon.get("phylum") or row_value(row, "phylum"),
            "class_field": taxon.get("class_field") or row_class_value(row),
            "order": taxon.get("order"),
            "family": taxon.get("family") or row_value(row, "family"),
            "genus": taxon.get("genus"),
            "taxonRank": taxon.get("taxonRank")
            or lowercase_taxon_rank(row_value(row, "taxonRank")),
            "acceptedNameUsageID": taxon.get("acceptedNameUsageID"),
        }

    existing_ids = set()
    if not truncate:
        existing_ids = set(
            IptCrabOccurrenceExtension.objects.values_list("occurrenceID", flat=True)
        )

    created_count = 0
    updated_count = 0

    if dry_run:
        for occurrence_id in occurrence_payloads:
            if occurrence_id in existing_ids:
                updated_count += 1
            else:
                created_count += 1
    else:
        with transaction.atomic():
            if truncate:
                table_name = IptCrabOccurrenceExtension._meta.db_table
                with connection.cursor() as cursor:
                    cursor.execute(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY;')

            for occurrence_id, payload in occurrence_payloads.items():
                _, created = IptCrabOccurrenceExtension.objects.update_or_create(
                    occurrenceID=occurrence_id,
                    defaults=payload.copy(),
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

    return {
        "dry_run": dry_run,
        "truncate": truncate,
        "source_records": queryset.count(),
        "synced_occurrences": len(occurrence_payloads),
        "skipped_no_occurrence_id": skipped_no_occurrence_id,
        "skipped_no_scientific_name": skipped_no_scientific_name,
        "taxon_names_requested": len(requested_taxon_names),
        "taxon_names_matched": len(
            {name for name in requested_taxon_names if name in taxon_map}
        ),
        "taxon_lookup_errors": len(taxon_lookup_errors),
        "created": created_count,
        "updated": updated_count,
    }
