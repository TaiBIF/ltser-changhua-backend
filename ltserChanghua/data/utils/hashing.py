import hashlib
import json


def compute_data_hash(payload):
    """
    將「代表資料內容」的欄位做成穩定字串，計算 SHA-256。
    用途：
    - 新匯入時計算 hash
    - 與 DB 既有 hash 比對
    - hash 相同 → 代表內容相同 → 不更新（updated_at 不會變）
    - hash 不同 → 代表內容變了 → 才更新
    """
    # json.dumps(sort_keys=True) 讓 key 順序固定，不會因 dict 順序不同導致 hash 改變
    # default=str 讓 date/Decimal 等型別可被轉為字串（避免 dumps 失敗）
    stable = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()
