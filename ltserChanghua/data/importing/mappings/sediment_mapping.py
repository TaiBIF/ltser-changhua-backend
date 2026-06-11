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


def build_sediment_payload(record, validators):
    """
    將 CKAN datastore record 轉成 Sediment 可用的 payload(dict)。
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
    soilTemperature = validators["decimal"](
        record.get("soilTemperature"), "soilTemperature", record, errors, warnings
    )
    tidalPoolSalinity = validators["decimal"](
        record.get("tidalPoolSalinity"),
        "tidalPoolSalinity",
        record,
        errors,
        warnings,
    )
    soilWater = validators["decimal"](
        record.get("soilWater"), "soilWater", record, errors, warnings
    )
    soilOrganicMatter = validators["decimal"](
        record.get("soilOrganicMatter"),
        "soilOrganicMatter",
        record,
        errors,
        warnings,
    )
    soilPH = validators["decimal"](
        record.get("soilPH"), "soilPH", record, errors, warnings
    )
    medianGrainSize = validators["decimal"](
        record.get("medianGrainSize"), "medianGrainSize", record, errors, warnings
    )
    sortingCoefficient = validators["decimal"](
        record.get("sortingCoefficient"),
        "sortingCoefficient",
        record,
        errors,
        warnings,
    )

    if soilPH is not None and not 0 <= soilPH <= 14:
        _push_error(
            errors,
            field="soilPH",
            error="out_of_range",
            value=soilPH,
            expected="0 <= soilPH <= 14",
        )

    payload = {
        "dataID": _clean_text(dataID),
        "eventDate": eventDate,
        "locationID": _clean_text(locationID),
        "soilTemperature": soilTemperature,
        "tidalPoolSalinity": tidalPoolSalinity,
        "soilWater": soilWater,
        "soilOrganicMatter": soilOrganicMatter,
        "soilPH": soilPH,
        "medianGrainSize": medianGrainSize,
        "sortingCoefficient": sortingCoefficient,
    }

    return payload, errors, warnings
