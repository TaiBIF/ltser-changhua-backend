def _clean_text(value):
    if value is None:
        return None
    return str(value).strip()


def _push_error(errors, *, field, error, value=None, expected=None):
    item = {"field": field, "error": error}
    if value is not None:
        item["value"] = value
    if expected is not None:
        item["expected"] = expected
    errors.append(item)


def build_waterquality_payload(record, validators):
    """
    將 CKAN datastore record 轉成 WaterQuality 可用的 payload(dict)。
    回傳：payload, row_errors, row_warnings
    """
    errors = []
    warnings = []

    # 必填欄位
    dataID = validators["required"](record.get("dataID"), "dataID", record, errors)
    locationID = validators["required"](
        record.get("locationID"), "locationID", record, errors
    )

    # 日期
    eventDate = validators["event_date"](
        record.get("eventDate"), "eventDate", record, errors
    )

    # 數值欄位
    waterTemperature = validators["decimal"](
        record.get("waterTemperature"),
        "waterTemperature",
        record,
        errors,
        warnings,
    )
    pH = validators["decimal"](record.get("pH"), "pH", record, errors, warnings)
    hydrogenIon = validators["decimal"](
        record.get("hydrogenIon"), "hydrogenIon", record, errors, warnings
    )
    oxidationReductionPotential = validators["decimal"](
        record.get("oxidationReductionPotential"),
        "oxidationReductionPotential",
        record,
        errors,
        warnings,
    )
    conductivity = validators["decimal"](
        record.get("conductivity"), "conductivity", record, errors, warnings
    )
    turbidity = validators["decimal"](
        record.get("turbidity"), "turbidity", record, errors, warnings
    )
    dissolvedOxygen = validators["decimal"](
        record.get("dissolvedOxygen"), "dissolvedOxygen", record, errors, warnings
    )
    totalDissolvedSolids = validators["decimal"](
        record.get("totalDissolvedSolids"),
        "totalDissolvedSolids",
        record,
        errors,
        warnings,
    )
    salinity = validators["decimal"](
        record.get("salinity"), "salinity", record, errors, warnings
    )
    specificGravity = validators["decimal"](
        record.get("specificGravity"), "specificGravity", record, errors, warnings
    )

    if pH is not None and not 0 <= pH <= 14:
        _push_error(
            errors,
            field="pH",
            error="out_of_range",
            value=pH,
            expected="0 <= pH <= 14",
        )

    payload = {
        "dataID": _clean_text(dataID),
        "eventDate": eventDate,
        "locationID": _clean_text(locationID),
        "waterTemperature": waterTemperature,
        "pH": pH,
        "hydrogenIon": hydrogenIon,
        "oxidationReductionPotential": oxidationReductionPotential,
        "conductivity": conductivity,
        "turbidity": turbidity,
        "dissolvedOxygen": dissolvedOxygen,
        "totalDissolvedSolids": totalDissolvedSolids,
        "salinity": salinity,
        "specificGravity": specificGravity,
    }

    return payload, errors, warnings
