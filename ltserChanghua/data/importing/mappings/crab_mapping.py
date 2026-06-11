BASIS_OF_RECORD_VALUES = {
    "MaterialEntity",
    "PreservedSpecimen",
    "FossilSpecimen",
    "LivingSpecimen",
    "HumanObservation",
    "MaterialSample",
    "MachineObservation",
    "Event",
    "Taxon",
    "Occurrence",
    "MaterialCitation",
}


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


def _validate_range(errors, field, value, min_value, max_value):
    if value is not None and not min_value <= value <= max_value:
        _push_error(
            errors,
            field=field,
            error="out_of_range",
            value=value,
            expected=f"{min_value} <= {field} <= {max_value}",
        )


def build_crab_payload(record, validators):
    """
    將 CKAN datastore record 轉成 Crab 可用的 payload(dict)。
    回傳：payload, row_errors, row_warnings
    """
    errors = []
    warnings = []

    # 必填欄位
    dataID = validators["required"](record.get("dataID"), "dataID", record, errors)
    basisOfRecord = validators["required"](
        record.get("basisOfRecord"), "basisOfRecord", record, errors
    )
    scientificName = validators["required"](
        record.get("scientificName"), "scientificName", record, errors
    )
    vernacularName = validators["required"](
        record.get("vernacularName"), "vernacularName", record, errors
    )
    locality = validators["required"](
        record.get("locality"), "locality", record, errors
    )
    locationID = validators["required"](
        record.get("locationID"), "locationID", record, errors
    )
    geodeticDatum = validators["required"](
        record.get("geodeticDatum"), "geodeticDatum", record, errors
    )

    # 日期
    eventDate = validators["event_date"](
        record.get("eventDate"), "eventDate", record, errors
    )

    validators["required"](
        record.get("individualCount"), "individualCount", record, errors
    )
    validators["required"](
        record.get("decimalLatitude"), "decimalLatitude", record, errors
    )
    validators["required"](
        record.get("decimalLongitude"), "decimalLongitude", record, errors
    )

    # 數值欄位
    individualCount = validators["int"](
        record.get("individualCount"), "individualCount", record, errors
    )
    decimalLatitude = validators["decimal"](
        record.get("decimalLatitude"),
        "decimalLatitude",
        record,
        errors,
        warnings,
    )
    decimalLongitude = validators["decimal"](
        record.get("decimalLongitude"),
        "decimalLongitude",
        record,
        errors,
        warnings,
    )
    sampleSizeValue = validators["decimal"](
        record.get("sampleSizeValue"),
        "sampleSizeValue",
        record,
        errors,
        warnings,
    )

    basisOfRecord = _clean_text(basisOfRecord)
    if basisOfRecord and basisOfRecord not in BASIS_OF_RECORD_VALUES:
        _push_error(
            errors,
            field="basisOfRecord",
            error="invalid_choice",
            value=basisOfRecord,
            expected=", ".join(sorted(BASIS_OF_RECORD_VALUES)),
        )

    _validate_range(errors, "individualCount", individualCount, 0, 9999)
    _validate_range(errors, "decimalLatitude", decimalLatitude, -90, 90)
    _validate_range(errors, "decimalLongitude", decimalLongitude, -180, 180)

    payload = {
        "dataID": _clean_text(dataID),
        "eventDate": eventDate,
        "basisOfRecord": basisOfRecord,
        "scientificName": _clean_text(scientificName),
        "vernacularName": _clean_text(vernacularName),
        "individualCount": individualCount,
        "locality": _clean_text(locality),
        "locationID": _clean_text(locationID),
        "decimalLatitude": decimalLatitude,
        "decimalLongitude": decimalLongitude,
        "geodeticDatum": _clean_text(geodeticDatum),
        "samplingProtocol": _clean_text(record.get("samplingProtocol")),
        "sampleSizeValue": sampleSizeValue,
        "sampleSizeUnit": _clean_text(record.get("sampleSizeUnit")),
        "samplingEffort": _clean_text(record.get("samplingEffort")),
    }

    return payload, errors, warnings
