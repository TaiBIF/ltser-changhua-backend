import re
from datetime import datetime


def _push_error(errors, *, field, error, value=None, expected=None, extra=None):
    item = {"field": field, "error": error}
    if value is not None:
        item["value"] = value
    if expected is not None:
        item["expected"] = expected
    if extra:
        item.update(extra)
    errors.append(item)


# 允許格式：YYYY / YYYY-MM / YYYY-MM-DD（你目前 eventDate 規則其實只收 YYYY-MM-DD）
RE_YEAR = re.compile(r"^\d{4}$")
RE_MONTH = re.compile(r"^\d{4}-\d{2}$")
RE_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")

RE_DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def validate_required(value, field_name, record, errors):
    """
    必填欄位檢查：None 或空字串都算缺值。
    - errors 是 list，用來收集錯誤訊息
    - 回傳 value（便於 pipeline 鏈式寫法）
    """
    if value is None:
        _push_error(errors, field=field_name, error="required")
        return value

    if isinstance(value, str) and not value.strip():
        _push_error(errors, field=field_name, error="required", value=value)
        return value

    return value


def validate_decimal(value, field_name, record, errors, warnings):
    """
    將數字欄位轉成 float。
    - 空值（None / "" / "NA"）→ 回傳 None（因為欄位可選）
    - 無法轉換 → 記 error，回傳 None
    - 額外防呆：NaN/Inf → 記 error，回傳 None
    """
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value or value.upper() == "NA":
            return None

    try:
        x = float(value)
    except Exception:
        _push_error(
            errors,
            field=field_name,
            error="not_a_number",
            value=value,
            expected="decimal number",
        )
        return None

    # NaN/Inf
    if x != x:
        _push_error(errors, field=field_name, error="nan", value=value)
        return None
    if x == float("inf") or x == float("-inf"):
        _push_error(errors, field=field_name, error="infinite", value=value)
        return None

    return x


def validate_event_date(value, field_name, record, errors):
    """
    規則：
    - 可包含時間（YYYY-MM-DDTHH:MM:SS...）
    - 只要能抓到 YYYY-MM-DD 並解析成功就合法
    - 不接受空值（必填）
    """
    if value is None:
        _push_error(errors, field=field_name, error="required")
        return None

    if isinstance(value, str) and not value.strip():
        _push_error(errors, field=field_name, error="required", value=value)
        return None

    s = str(value).strip()

    m = RE_DATE_PREFIX.match(s)
    if not m:
        _push_error(
            errors,
            field=field_name,
            error="invalid_format",
            value=s,
            expected="YYYY-MM-DD or ISO datetime",
        )
        return None

    date_part = m.group(1)

    try:
        return datetime.strptime(date_part, "%Y-%m-%d").date()
    except Exception:
        _push_error(
            errors,
            field=field_name,
            error="invalid_date",
            value=date_part,
            expected="valid calendar date",
        )
        return None


def validate_int(value, field_name, record, errors):
    """
    將欄位轉成 int（必須是整數）
    規則：
    - None / "" / "null" → error: required
    - 無法轉成數字 → error
    - 可轉成數字但不是整數 → error
    """
    if value in (None, "", "null"):
        _push_error(errors, field=field_name, error="required")
        return None

    try:
        x = float(value)
    except Exception:
        _push_error(
            errors,
            field=field_name,
            error="not_a_number",
            value=value,
            expected="integer",
        )
        return None

    # NaN / Inf
    if x != x or x in (float("inf"), float("-inf")):
        _push_error(
            errors,
            field=field_name,
            error="invalid_number",
            value=value,
            expected="integer",
        )
        return None

    if not x.is_integer():
        _push_error(
            errors,
            field=field_name,
            error="not_integer",
            value=value,
            expected="integer",
        )
        return None

    return int(x)


def validate_int_optional(value, field_name, record, errors):
    """
    將欄位轉成 int（可為空值）
    規則：
    - None / "" / "null" → 回傳 None（不報錯）
    - 無法轉成數字 → error
    - 可轉成數字但不是整數 → error
    """
    if value in (None, "", "null"):
        return None

    try:
        x = float(value)
    except Exception:
        _push_error(
            errors,
            field=field_name,
            error="not_a_number",
            value=value,
            expected="integer",
        )
        return None

    # NaN / Inf
    if x != x or x in (float("inf"), float("-inf")):
        _push_error(
            errors,
            field=field_name,
            error="invalid_number",
            value=value,
            expected="integer",
        )
        return None

    if not x.is_integer():
        _push_error(
            errors,
            field=field_name,
            error="not_integer",
            value=value,
            expected="integer",
        )
        return None

    return int(x)


def validate_event_datetime(value, field_name, record, errors):
    """
    將日期/時間欄位解析為 datetime（可選）
    支援：
    - ISO datetime: 2023-03-10T00:00:00 / ...Z / ...+08:00
    - 'YYYY-MM-DD HH:MM:SS'
    - 若只有日期或只抓到日期前綴：轉成當天 00:00:00
    規則：
    - None / "" → 回傳 None
    - 解析失敗 → error，回傳 None
    """
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None

    s = str(value).strip()

    # 1) 先嘗試直接 parse（處理大多 ISO）
    try:
        # Python 的 fromisoformat 不吃 'Z'，先替換
        iso = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(iso)
        return dt
    except Exception:
        pass

    # 2) 'YYYY-MM-DD HH:MM:SS'
    try:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        return dt
    except Exception:
        pass

    # 3) 只抓日期前綴 → 當天 00:00:00
    m = RE_DATE_PREFIX.match(s)
    if not m:
        _push_error(
            errors,
            field=field_name,
            error="invalid_format",
            value=s,
            expected="ISO datetime or YYYY-MM-DD HH:MM:SS",
        )
        return None

    date_part = m.group(1)
    try:
        d = datetime.strptime(date_part, "%Y-%m-%d")
        return d  # already datetime at 00:00:00
    except Exception:
        _push_error(
            errors,
            field=field_name,
            error="invalid_date",
            value=date_part,
            expected="valid calendar date",
        )
        return None


def validate_boolean(value, field_name, record, errors):
    """
    將欄位轉成 boolean（必填）
    規則：
    - None / "" / "null" → error: required
    - 可接受的 true 值：
        True, 1, "1", "true", "yes", "y", "是"
    - 可接受的 false 值：
        False, 0, "0", "false", "no", "n", "否"
    """
    if value in (None, "", "null"):
        _push_error(errors, field=field_name, error="required")
        return None

    # 已是 boolean
    if isinstance(value, bool):
        return value

    # 數字
    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False

    # 字串
    if isinstance(value, str):
        v = value.strip().lower()

        TRUE_VALUES = {"true", "1", "yes", "y", "是"}
        FALSE_VALUES = {"false", "0", "no", "n", "否"}

        # 注意：中文不會被 lower 影響
        if v in TRUE_VALUES:
            return True
        if v in FALSE_VALUES:
            return False

    _push_error(
        errors,
        field=field_name,
        error="not_boolean",
        value=value,
        expected="boolean",
    )
    return None


def validate_boolean_optional(value, field_name, record, errors):
    """
    將欄位轉成 boolean（選填）
    規則：
    - None / "" / "null" → 回傳 None（不報錯）
    - 可接受的 true 值：
        True, 1, "1", "true", "yes", "y", "是"
    - 可接受的 false 值：
        False, 0, "0", "false", "no", "n", "否"
    """
    if value in (None, "", "null"):
        return None

    # 已是 boolean
    if isinstance(value, bool):
        return value

    # 數字
    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False

    # 字串
    if isinstance(value, str):
        v = value.strip().lower()

        TRUE_VALUES = {"true", "1", "yes", "y", "是"}
        FALSE_VALUES = {"false", "0", "no", "n", "否"}

        if v in TRUE_VALUES:
            return True
        if v in FALSE_VALUES:
            return False

    _push_error(
        errors,
        field=field_name,
        error="not_boolean",
        value=value,
        expected="boolean",
    )
    return None
