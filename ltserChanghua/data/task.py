import os
import requests
from datetime import datetime
from celery import shared_task

# from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings


from data.importing.importer import import_ckan_resource
from data.importing.registry import ADAPTERS
from data.utils.ipt_sync import sync_crab_events, sync_crab_occurrence_extensions

IPT_OBSERVATION_ITEMS = {"蟹類調查"}
IPT_SYNC_LOCK_KEY = "ipt_sync_lock"
IPT_SYNC_LOCK_TIMEOUT = 60 * 30

ERROR_PROBLEM_LABELS = {
    # 通用
    "required": "必填欄位缺值（不可為空白）",
    # 數值/整數
    "not_a_number": "資料非數值（無法解析成數字）",
    "invalid_number": "數值不合法（NaN 或無限大，無法作為有效數字）",
    "nan": "數值為 NaN（非有效數字）",
    "infinite": "數值為無限大（Inf/-Inf，非有效數字）",
    "not_integer": "資料非整數（必須為整數）",
    # 日期/時間
    "invalid_format": "格式不正確（建議使用 YYYY-MM-DD 格式）",
    "invalid_date": "日期不合法（非有效日期）",
    # 布林
    "not_boolean": "資料非布林值（需為 True/False 或 0/1、是/否）",
}


def format_slack_ipt_sync_lines(report):
    ipt_sync = report.get("ipt_sync") or {}
    if not ipt_sync:
        return []

    if ipt_sync.get("skipped"):
        reason = ipt_sync.get("reason", "unknown")
        if reason == "not_aquaticfauna":
            return []
        return ["", "IPT sync:", f"skipped: {reason}"]

    occurrence_result = ipt_sync.get("occurrence_extension") or {}
    event_result = ipt_sync.get("event") or {}

    return [
        "",
        "IPT sync:",
        f"event_core.synced: {event_result.get('synced_events', 0)}",
        f"event_core.created: {event_result.get('created', 0)}",
        f"event_core.updated: {event_result.get('updated', 0)}",
        f"occurrence_extension.synced: {occurrence_result.get('synced_occurrences', 0)}",
        f"occurrence_extension.created: {occurrence_result.get('created', 0)}",
        f"occurrence_extension.updated: {occurrence_result.get('updated', 0)}",
    ]


def format_slack_text(
    report, site=None, observation_item=None, resource_name=None, task_id=None
):
    rid = report.get("resource_id", "(unknown)")
    fatal = report.get("fatal_errors") or []

    title_left = site or "(unknown site)"
    title_right = observation_item or "(unknown observation)"
    rn = resource_name or report.get("resource_name") or "(unknown)"

    lines = [
        f"{title_left}｜{title_right}",
        f"resource_name: {rn}",
        f"resource_id: {rid}",
        f"task_id: {task_id or '(unknown)'}",
        "",
        f"records_seen: {report.get('records_seen', 0)} / total: {report.get('total')}",
        f"inserted: {report.get('inserted', 0)}",
        f"updated: {report.get('updated', 0)}",
        f"skipped: {report.get('skipped', 0)}",
        f"row_errors: {report.get('row_errors', 0)}",
        f"row_warnings: {report.get('row_warnings', 0)}",
        f"fatal_errors: {len(fatal)}",
    ]

    lines += format_slack_ipt_sync_lines(report)

    if fatal:
        sample = "\n".join([str(x) for x in fatal[:3]])
        lines += ["", "⚠️ Fatal sample:", sample]

    body = "\n".join(lines)

    return f"*[Changhua]*\n\n匯入驗證結果\n```{body}```"


def to_taipei_time(dt_str):
    if not dt_str:
        return None

    dt = datetime.fromisoformat(dt_str)  # 解析 ISO 8601
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.utc)

    taipei_tz = timezone.get_fixed_timezone(480)  # UTC+8
    return dt.astimezone(taipei_tz)


def parse_error_key(key):
    """
    將 'time.invalid_format' 拆成 ('time', 'invalid_format')
    若格式不符，全部當成 problem
    """
    if "." in key:
        field, problem = key.split(".", 1)
    else:
        field, problem = key, "unknown"
    return field, problem


def format_error_breakdown(report, max_items=10):
    breakdown = report.get("error_breakdown") or {}
    if not breakdown:
        return ""

    items = sorted(breakdown.items(), key=lambda kv: kv[1], reverse=True)[:max_items]

    lines = []
    lines.append("──────────────────────────")
    lines.append("⚠️ 匯入錯誤摘要")
    lines.append("──────────────────────────")
    lines.append(
        "本次資料匯入未能成功完成。\n"
        "請子計畫負責人依下列錯誤說明修正原始資料後，\n"
        "重新將修改完成的資料集上傳至 Depositar，系統將再自動排程處理。\n"
    )
    lines.append("【錯誤類型統計】")

    for key, count in items:
        field, problem = parse_error_key(key)
        lines.append(f"- 欄位：{field}")
        label = ERROR_PROBLEM_LABELS.get(problem, problem)
        lines.append(f"      問題：{label}")
        lines.append(f"      影響筆數：{count} 筆")

    lines.append("")
    return "\n".join(lines)


def format_fatal_hint(report):
    fatal_errors = report.get("fatal_errors") or []
    if not fatal_errors:
        return ""

    fe = fatal_errors[0] or {}
    code = fe.get("error", "")
    exc = fe.get("exception", "")

    if (
        code == "db_write_failed"
        and "bulk_update() objects must have a primary key set" in exc
    ):
        return (
            "──────────────────────────\n"
            "⚠️ 重要提醒：可能為 dataID 重複\n"
            "──────────────────────────\n"
            "系統在寫入資料庫時失敗。此狀況通常是資料中的 dataID（或唯一識別欄位）出現重複值，\n"
            "導致系統無法正確更新資料。\n\n"
            "dataID 重複可能發生在以下情況：\n"
            "1) 同一個資料集內部，存在重複的 dataID\n"
            "2) 本次上傳的資料，其 dataID 與站點中既有資料集的 dataID 發生重複\n\n"
        )

    return (
        "──────────────────────────\n"
        "⚠️ 系統錯誤提示\n"
        "──────────────────────────\n"
        "本次匯入過程發生系統錯誤，未完成寫入。\n"
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def import_ckan_and_notify(
    self,
    package_name,
    resource_id,
    base_url,
    site=None,
    observation_item=None,
    resource_name=None,
    limit=100,
    notify_slack=True,
):
    adapter_cls = ADAPTERS.get(package_name)
    if not adapter_cls:
        raise ValueError("unknown_dataset: %s" % package_name)

    adapter = adapter_cls()
    report = import_ckan_resource(
        resource_id=resource_id,
        base_url=base_url,
        limit=limit,
        adapter=adapter,
    )

    report["celery_task_id"] = self.request.id

    if notify_slack:
        webhook = os.environ.get("SLACK_WEBHOOK_URL")
    else:
        webhook = None

    if webhook:
        try:
            text = format_slack_text(
                report,
                site=site,
                observation_item=observation_item,
                resource_name=resource_name,
                task_id=self.request.id,
            )
            requests.post(webhook, json={"text": text}, timeout=10)
        except Exception:
            pass

    return report


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_import_slack(
    self,
    report,
    *,
    site=None,
    observation_item=None,
    resource_name=None,
):
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        return report

    text = format_slack_text(
        report,
        site=site,
        observation_item=observation_item,
        resource_name=resource_name,
        task_id=report.get("celery_task_id") or self.request.id,
    )
    requests.post(webhook, json={"text": text}, timeout=10)
    return report


def is_successful_import(report):
    return (
        not report.get("fatal_errors")
        and (report.get("row_errors") or 0) == 0
        and (report.get("row_warnings") or 0) == 0
    )


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def sync_ipt_crab_after_success(
    self,
    report,
    *,
    observation_item=None,
):
    if observation_item not in IPT_OBSERVATION_ITEMS:
        report["ipt_sync"] = {"skipped": True, "reason": "not_ipt_observation_items"}
        return report

    if not is_successful_import(report):
        report["ipt_sync"] = {"skipped": True, "reason": "import_not_successful"}
        return report

    lock_acquired = cache.add(
        IPT_SYNC_LOCK_KEY,
        self.request.id,
        timeout=IPT_SYNC_LOCK_TIMEOUT,
    )
    if not lock_acquired:
        report["ipt_sync"] = {
            "skipped": True,
            "reason": "sync_already_running",
        }
        return report

    try:
        occurrence_result = sync_crab_occurrence_extensions()
        event_result = sync_crab_events()

        report["ipt_sync"] = {
            "skipped": False,
            "celery_task_id": self.request.id,
            "occurrence_extension": occurrence_result,
            "event": event_result,
        }
    finally:
        cache.delete(IPT_SYNC_LOCK_KEY)

    return report


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_import_email(
    self,
    report,  # 接到 import_ckan_and_notify 的 return report
    *,
    to_emails,
    cc_emails=None,
    observation_item=None,
    resource_name=None,
    task_id=None,
):
    root_id = getattr(self.request, "root_id", None) or task_id
    if root_id:
        dedupe_key = f"import_email_sent:{root_id}"
        if not cache.add(dedupe_key, "1", timeout=60 * 60 * 24 * 7):
            return {"skipped": True, "reason": "duplicate"}

    if not to_emails:
        return {"skipped": True, "reason": "to_email_missing"}

    row_errors = report.get("row_errors", 0)
    row_warnings = report.get("row_warnings", 0)

    inserted = report.get("inserted", 0)
    updated = report.get("updated", 0)
    skipped = report.get("skipped", 0)

    records_seen = report.get("records_seen", 0)
    total = report.get("total", 0)

    started_at = report.get("started_at")
    finished_at = report.get("finished_at")

    started_at_tw = to_taipei_time(started_at)
    finished_at_tw = to_taipei_time(finished_at)

    started_at_str = (
        started_at_tw.strftime("%Y-%m-%d %H:%M:%S") if started_at_tw else "—"
    )
    finished_at_str = (
        finished_at_tw.strftime("%Y-%m-%d %H:%M:%S") if finished_at_tw else "—"
    )

    task_id_in_report = report.get("celery_task_id")

    error_section = format_error_breakdown(report)
    fatal_hint = format_fatal_hint(report)
    ipt_sync = report.get("ipt_sync") or {}
    ipt_sync_section = ""
    if ipt_sync and not ipt_sync.get("skipped"):
        occurrence_result = ipt_sync.get("occurrence_extension") or {}
        event_result = ipt_sync.get("event") or {}
        ipt_sync_section = (
            "\n"
            "──────────────────────────\n"
            "IPT 同步結果\n"
            "──────────────────────────\n"
            f"Event core 同步筆數：{event_result.get('synced_events', 0)}\n"
            f"Event core 新增/更新：{event_result.get('created', 0)} / {event_result.get('updated', 0)}\n\n"
            f"Occurrence extension 同步筆數：{occurrence_result.get('synced_occurrences', 0)}\n"
            f"Occurrence extension 新增/更新：{occurrence_result.get('created', 0)} / {occurrence_result.get('updated', 0)}\n"
            "\n"
            "後續請至 IPT 資料集管理頁面確認資料集內容。\n"
            "進入該資料集後，可於 Source Data 區塊點擊 Save，讓 IPT 重新讀取並套用最新同步資料；\n"
            "確認資料無誤後，再至 Publication 區塊發布新版資料集。\n"
        )

    fatal_errors = report.get("fatal_errors") or []

    status_tag = "成功"
    if fatal_errors:
        status_tag = "失敗（系統寫入錯誤）"
    elif row_errors and (inserted == 0 and updated == 0):
        status_tag = "失敗（資料格式錯誤）"
    elif row_errors:
        status_tag = "完成但有錯誤"
    elif row_warnings:
        status_tag = "完成但有警告"

    if status_tag == "成功":
        subject = (
            f"臺灣長期社會生態核心觀測站 彰化站 | {resource_name} 資料已匯入至站點網站"
        )
    else:
        subject = f"臺灣長期社會生態核心觀測站 彰化站 | {resource_name} 資料匯入至站點網站 {status_tag}"

    if fatal_errors:
        intro = (
            f"您好，\n\n"
            f"您所負責的「{observation_item}」子計畫中，\n"
            f"資料集「{resource_name}」匯入至網站資料庫時發生錯誤，未完成寫入。\n\n"
            f"如需確認站點目前資料狀態，可至下列網址查看：\n"
            f"https://ltsertwlyudao.org/\n\n"
        )
    else:
        intro = (
            f"您好，\n\n"
            f"您所負責的「{observation_item}」子計畫中，\n"
            f"資料集「{resource_name}」已匯入至網站資料庫中。\n\n"
            f"最新資料可至下列網址查看：\n"
            f"https://ltsertwlyudao.org/\n\n"
        )

    body = intro + (
        f"──────────────────────────\n"
        f"本次資料匯入統計摘要\n"
        f"──────────────────────────\n"
        f"插入筆數：{inserted}\n"
        f"更新筆數：{updated}\n"
        f"略過筆數：{skipped}\n"
        f"錯誤筆數：{row_errors}\n"
        f"警告筆數：{row_warnings}\n\n"
        f"資料總筆數：{total}\n"
        f"實際處理筆數：{records_seen}\n\n"
        f"匯入開始時間：{started_at_str}\n"
        f"匯入完成時間：{finished_at_str}\n\n"
        f"【資料狀態說明】\n"
        f"插入筆數：成功新增至資料庫中的資料筆數\n"
        f"更新筆數：已存在於資料庫中，且部分內容被更新的資料筆數\n"
        f"略過筆數：資料已存在於資料庫，且內容無異動而未進行新增或更新的筆數\n"
        f"錯誤筆數：因格式或內容錯誤而無法匯入，且未寫入資料庫的資料筆數\n"
        f"警告筆數：資料可成功匯入，但內容可能需人工確認的資料筆數\n"
        f"{ipt_sync_section}"
        f"{fatal_hint}"
        f"{error_section}"
        f"\n"
        f"──────────────────────────\n"
        f"本信件為系統自動發送，若有任何疑問請直接回覆信件。\n"
        f"task ID: {task_id_in_report}\n"
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=to_emails,
        cc=cc_emails,
    )
    email.send(fail_silently=False)

    return {"sent": True}
