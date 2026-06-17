DEFAULT_TO = ["nil158320@gmail.com"]
DEFAULT_CC = ["b9120504@cc.ncue.edu.tw", "sfwang@cc.ncue.edu.tw", "jhujyunjhang@gmail.com"]

OBSERVATION_EMAILS = {}


def get_email_targets(observation_item):
    """
    回傳 (to_list, cc_list, bcc_list)
    - observation_item 若找不到，回退到 DEFAULT_*
    - 支援 OBSERVATION_EMAILS 裡面只填 to/cc/bcc 任一項
    """
    cfg = OBSERVATION_EMAILS.get(observation_item or "", {})
    to = cfg.get("to") or DEFAULT_TO
    cc = cfg.get("cc") or DEFAULT_CC

    if isinstance(to, str):
        to = [to]
    if isinstance(cc, str):
        cc = [cc]

    return to, cc
