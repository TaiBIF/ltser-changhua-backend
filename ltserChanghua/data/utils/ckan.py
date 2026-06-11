import requests


def datastore_search(resource_id, base_url, offset, limit):
    """
    呼叫 CKAN datastore_search 取得 records 分頁。
    """
    url = base_url.rstrip("/") + "/api/3/action/datastore_search"
    resp = requests.get(
        url, params={"resource_id": resource_id, "offset": offset, "limit": limit}
    )

    if resp.status_code != 200:
        return None, {
            "error": "datastore_search_failed",
            "resource_id": resource_id,
            "status_code": resp.status_code,
            "text": resp.text,
        }

    data = resp.json()
    result = data.get("result", {})
    return {
        "records": result.get("records", []),
        "total": result.get("total", 0),
    }, None
