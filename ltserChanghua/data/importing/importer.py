from django.utils import timezone

from data.utils.ckan import datastore_search


def bump_error_breakdown(breakdown, row_errors):
    for e in row_errors or []:
        field = e.get("field") or "unknown_field"
        code = e.get("error") or "unknown_error"
        key = "%s.%s" % (field, code)
        breakdown[key] = breakdown.get(key, 0) + 1


def is_blank_record(record, fields=None):
    if fields:
        values = (record.get(field) for field in fields)
    else:
        values = (
            value for field, value in record.items() if not field.startswith("_")
        )

    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return False
    return True


def import_ckan_resource(resource_id, base_url, limit, adapter):
    started_at = timezone.now()

    report = {
        "resource_id": resource_id,
        "started_at": started_at.isoformat(),
        "finished_at": None,
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "row_errors": 0,
        "row_warnings": 0,
        "errors_sample": [],
        "warnings_sample": [],
        "records_seen": 0,
        "total": None,
        "error_breakdown": {},
        "fatal_errors": [],
    }

    offset = 0

    while True:
        page, err = datastore_search(resource_id, base_url, offset, limit)
        if err:
            report["fatal_errors"].append(err)
            break

        records = page.get("records", [])
        total = page.get("total", 0)
        report["total"] = total

        if not records:
            if total and offset == 0:
                report["fatal_errors"].append(
                    {"error": "no_records_returned", "resource_id": resource_id}
                )
            break

        report["records_seen"] += len(records)

        ok_payloads = []
        for rec in records:
            blank_check_fields = getattr(adapter, "hash_fields", None)
            if is_blank_record(rec, blank_check_fields):
                report["skipped"] += 1
                continue

            payload, row_errors, row_warnings = adapter.build_payload(rec)

            if row_errors:
                report["row_errors"] += 1
                bump_error_breakdown(report["error_breakdown"], row_errors)

                if len(report["errors_sample"]) < 20:
                    row_ref = rec.get(adapter.key_field) or rec.get("dataID")
                    report["errors_sample"].append(
                        {"row_ref": row_ref, "errors": row_errors}
                    )

            if row_warnings:
                report["row_warnings"] += 1
                if len(report["warnings_sample"]) < 20:
                    report["warnings_sample"].append(row_warnings)

            if row_errors:
                continue

            ok_payloads.append(payload)

        if ok_payloads:
            key_field = adapter.key_field
            keys = []
            for p in ok_payloads:
                k = p.get(key_field)
                if k is not None:
                    keys.append(k)

            existing_map = adapter.fetch_existing_hash_map(keys)

            to_create = []
            to_update = []
            skipped = 0

            for p in ok_payloads:
                k = p.get(key_field)
                if k is None:
                    # payload 層不該發生，但保底
                    report["row_errors"] += 1
                    bump_error_breakdown(
                        report["error_breakdown"],
                        [{"field": key_field, "error": "required"}],
                    )
                    if len(report["errors_sample"]) < 20:
                        report["errors_sample"].append(
                            {
                                "row_ref": None,
                                "errors": [{"field": key_field, "error": "required"}],
                            }
                        )
                    continue

                h = adapter.compute_hash(p)

                existing = existing_map.get(k)

                if existing is None:
                    obj = adapter.make_instance(p)
                    obj.data_hash = h
                    to_create.append(obj)
                elif existing["data_hash"] != h:
                    obj = adapter.make_instance(p)
                    obj.pk = existing["id"]
                    obj.data_hash = h
                    to_update.append(obj)
                else:
                    skipped += 1

            try:
                adapter.write(to_create=to_create, to_update=to_update)
                report["inserted"] += len(to_create)
                report["updated"] += len(to_update)
                report["skipped"] += skipped
            except Exception as e:
                report["fatal_errors"].append(
                    {
                        "error": "db_write_failed",
                        "resource_id": resource_id,
                        "exception": str(e),
                    }
                )
                break

        offset += limit
        if report["records_seen"] >= (total or 0):
            break

    report["finished_at"] = timezone.now().isoformat()
    return report
