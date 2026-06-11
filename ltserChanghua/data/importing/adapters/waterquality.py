from django.db import transaction
from django.utils import timezone

from data.importing.mappings.waterquality_mapping import build_waterquality_payload
from data.models import WaterQuality
from data.utils.hashing import compute_data_hash
from data.utils.validators import (
    validate_decimal,
    validate_event_date,
    validate_required,
)

DEFAULT_WATERQUALITY_HASH_FIELDS = [
    "dataID",
    "eventDate",
    "locationID",
    "waterTemperature",
    "pH",
    "hydrogenIon",
    "oxidationReductionPotential",
    "conductivity",
    "turbidity",
    "dissolvedOxygen",
    "totalDissolvedSolids",
    "salinity",
    "specificGravity",
]


class WaterQualityAdapter:
    key_field = "dataID"

    def __init__(self, hash_fields=None):
        self.hash_fields = hash_fields or list(DEFAULT_WATERQUALITY_HASH_FIELDS)
        self.validators = {
            "required": validate_required,
            "decimal": validate_decimal,
            "event_date": validate_event_date,
        }

    def build_payload(self, record):
        return build_waterquality_payload(record, self.validators)

    def compute_hash(self, payload):
        hash_payload = {}
        for field in self.hash_fields:
            hash_payload[field] = payload.get(field)
        return compute_data_hash(hash_payload)

    def fetch_existing_hash_map(self, keys):
        if not keys:
            return {}

        return {
            data_id: {"id": pk, "data_hash": data_hash}
            for data_id, pk, data_hash in WaterQuality.objects.filter(
                dataID__in=keys
            ).values_list("dataID", "id", "data_hash")
        }

    def make_instance(self, payload):
        return WaterQuality(**payload)

    def write(self, to_create, to_update):
        now = timezone.now()

        for obj in to_update:
            obj.updated_at = now

        with transaction.atomic():
            if to_create:
                WaterQuality.objects.bulk_create(to_create, batch_size=1000)

            if to_update:
                WaterQuality.objects.bulk_update(
                    to_update,
                    fields=self.hash_fields + ["data_hash", "updated_at"],
                    batch_size=1000,
                )
