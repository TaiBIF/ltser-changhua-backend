from django.conf import settings
import requests
import xml.etree.ElementTree as ET
import json
from collections import defaultdict

# API 端點
URL = "https://segisws.moi.gov.tw/STATWSSTData/AdminService.asmx"

# API 認證資訊
API_CONFIG = {
    "oAPPId": settings.SEGISWS_API_ID,
    "oAPIKey": settings.SEGISWS_API_KEY,
    "oResultDataType": "JSON",  # 回應格式
}

# 查詢條件
QUERY_PARAMS = {
    "oFilterCountys": "10007",  # 彰化縣
    "oFilterTowns": "10007230",  # 芳苑鄉
    "oFilterVillages": "*",
}

API_MAPPING = {
    "village": {
        "unit_code": "U01VI",
        "api_name": "GetVillageSTData",
        "id_field": "V_ID",
        "filter_town": f"<oFilterTowns>{QUERY_PARAMS['oFilterTowns']}</oFilterTowns>",
        "filter_village": f"<oFilterVillages>{QUERY_PARAMS['oFilterVillages']}</oFilterVillages>",
    },
    "town": {
        "unit_code": "U01TO",
        "api_name": "GetTownSTData",
        "id_field": "TOWN_ID",
        "filter_town": "<oFilterTowns>*</oFilterTowns>",
        "filter_village": "",  # 鄉鎮級查詢不需要村里篩選
    },
}

THEME_MAPPING = {
    "summary": {
        "meta_code": "3A1FA_A1C1",
        "columns": "INFO_TIME,{id_field},H_CNT,P_CNT",
    },
    "index": {
        "meta_code": "3A1FA_A1C3",
        "columns": "INFO_TIME,{id_field},P_DEN,M_F_RAT,DEPENDENCY_RAT,A65_A0A14_RAT,A0A14_A15A65_RAT,A65UP_A15A64_RAT,A65_A0A14_RAT",
    },
    "dynamics_index": {  # 人口消長統計指標
        "meta_code": "3A1FA_A1B35",
        "columns": "INFO_TIME,{id_field},BORN_PER,DEAD_PER,NATURE_INC_PER,SOCIAL_INC_PER",
    },
    "structure": {  # 三段年齡組性別人口統計
        "meta_code": "3A1FA_A1C9",
        "columns": "INFO_TIME,{id_field},A0A14_CNT,A15A64_CNT,A65UP_CNT",
    },
    "pyramid": {"meta_code": "3A1FA_A1C5", "columns": "*"},
    "industry": {
        "meta_code": "3A75ED_A9C2",
        "columns": "*",
    },
    "fishing": {
        "meta_code": "37647DA_A8B14",
        "columns": "INFO_TIME,{id_field},COUNTY_ID,COUNTY,TOWN,COLUMN8,COLUMN9,COLUMN10,COLUMN11,COLUMN12,COLUMN13,COLUMN14",
    },
    "poultry": {
        "meta_code": "37647DA_A8B17",
        "columns": "INFO_TIME,{id_field},COUNTY_ID,COUNTY,TOWN,COLUMN2,COLUMN3,COLUMN5,COLUMN6,COLUMN7,COLUMN8",
    },
    "farming": {
        "meta_code": "37647DA_A8B18",
        "columns": "INFO_TIME,{id_field},COLUMN1,COLUMN2,COLUMN5",
    },
    "fruit": {
        "meta_code": "37647DA_A8B11",
        "columns": "INFO_TIME,{id_field},COLUMN1,COLUMN2",
    },
    "crop": {
        "meta_code": "37647DA_A8B12",
        "columns": "INFO_TIME,{id_field},COLUMN1,COLUMN2",
    },
    "special_crop": {
        "meta_code": "37647DA_A8C7",
        "columns": "INFO_TIME,{id_field},COLUMN1,COLUMN2",
    },
    "rice": {
        "meta_code": "37647DA_A8C4",
        "columns": "INFO_TIME,{id_field},COLUMN1,COLUMN2",
    },
    "livestock": {
        "meta_code": "37647DA_A8B15",
        "columns": "INFO_TIME,{id_field},COUNTY_ID,COUNTY,TOWN,COLUMN1,COLUMN2,COLUMN3,COLUMN4,COLUMN5,COLUMN6,COLUMN7",
    },
    "vege": {
        "meta_code": "37647DA_A8C9",
        "columns": "INFO_TIME,{id_field},COLUMN1,COLUMN2",
    },
}

VILLAGE_NAME_MAPPING = {
    "10007230-001": "芳苑村",
    "10007230-002": "芳中村",
    "10007230-003": "仁愛村",
    "10007230-004": "信義村",
    "10007230-005": "後寮村",
    "10007230-006": "三合村",
    "10007230-007": "永興村",
    "10007230-008": "五俊村",
    "10007230-009": "路上村",
    "10007230-010": "路平村",
    "10007230-011": "三成村",
    "10007230-012": "福榮村",
    "10007230-013": "頂廍村",
    "10007230-014": "新街村",
    "10007230-015": "王功村",
    "10007230-016": "博愛村",
    "10007230-017": "和平村",
    "10007230-018": "民生村",
    "10007230-019": "興仁村",
    "10007230-020": "新寶村",
    "10007230-021": "草湖村",
    "10007230-022": "文津村",
    "10007230-023": "建平村",
    "10007230-024": "崙腳村",
    "10007230-025": "新生村",
    "10007230-026": "漢寶村",
}

TOWN_NAME_MAPPING = {
    "10007010": "彰化市",
    "10007020": "鹿港鎮",
    "10007030": "和美鎮",
    "10007040": "線西鄉",
    "10007050": "伸港鄉",
    "10007060": "福興鄉",
    "10007070": "秀水鄉",
    "10007080": "花壇鄉",
    "10007090": "芬園鄉",
    "10007100": "員林市",
    "10007110": "溪湖鎮",
    "10007120": "田中鎮",
    "10007130": "大村鄉",
    "10007140": "埔鹽鄉",
    "10007150": "埔心鄉",
    "10007160": "永靖鄉",
    "10007170": "社頭鄉",
    "10007180": "二水鄉",
    "10007190": "北斗鎮",
    "10007200": "二林鎮",
    "10007210": "田尾鄉",
    "10007220": "埤頭鄉",
    "10007230": "芳苑鄉",
    "10007240": "大城鄉",
    "10007250": "竹塘鄉",
    "10007260": "溪州鄉",
}

PYRIMAD_KEY_MAPIING = {
    "COUNTY_ID": "縣市代碼",
    "COUNTY": "縣市名稱",
    "TOWN_ID": "鄉鎮市區代碼",
    "TOWN": "鄉鎮市區名稱",
    "V_ID": "村里代碼",
    "VILLAGE": "村里名稱",
    "A0A4_CNT": "0-4歲人口數",
    "A0A4_M_CNT": "0-4歲男性人口數",
    "A0A4_F_CNT": "0-4歲女性人口數",
    "A5A9_CNT": "5-9歲人口數",
    "A5A9_M_CNT": "5-9歲男性人口數",
    "A5A9_F_CNT": "5-9歲女性人口數",
    "A10A14_CNT": "10-14歲人口數",
    "A10A14_M_CNT": "10-14歲男性人口數",
    "A10A14_F_CNT": "10-14歲女性人口數",
    "A15A19_CNT": "15-19歲人口數",
    "A15A19_M_CNT": "15-19歲男性人口數",
    "A15A19_F_CNT": "15-19歲女性人口數",
    "A20A24_CNT": "20-24歲人口數",
    "A20A24_M_CNT": "20-24歲男性人口數",
    "A20A24_F_CNT": "20-24歲女性人口數",
    "A25A29_CNT": "25-29歲人口數",
    "A25A29_M_CNT": "25-29歲男性人口數",
    "A25A29_F_CNT": "25-29歲女性人口數",
    "A30A34_CNT": "30-34歲人口數",
    "A30A34_M_CNT": "30-34歲男性人口數",
    "A30A34_F_CNT": "30-34歲女性人口數",
    "A35A39_CNT": "35-39歲人口數",
    "A35A39_M_CNT": "35-39歲男性人口數",
    "A35A39_F_CNT": "35-39歲女性人口數",
    "A40A44_CNT": "40-44歲人口數",
    "A40A44_M_CNT": "40-44歲男性人口數",
    "A40A44_F_CNT": "40-44歲女性人口數",
    "A45A49_CNT": "45-49歲人口數",
    "A45A49_M_CNT": "45-49歲男性人口數",
    "A45A49_F_CNT": "45-49歲女性人口數",
    "A50A54_CNT": "50-54歲人口數",
    "A50A54_M_CNT": "50-54歲男性人口數",
    "A50A54_F_CNT": "50-54歲女性人口數",
    "A55A59_CNT": "55-59歲人口數",
    "A55A59_M_CNT": "55-59歲男性人口數",
    "A55A59_F_CNT": "55-59歲女性人口數",
    "A60A64_CNT": "60-64歲人口數",
    "A60A64_M_CNT": "60-64歲男性人口數",
    "A60A64_F_CNT": "60-64歲女性人口數",
    "A65A69_CNT": "65-69歲人口數",
    "A65A69_M_CNT": "65-69歲男性人口數",
    "A65A69_F_CNT": "65-69歲女性人口數",
    "A70A74_CNT": "70-74歲人口數",
    "A70A74_M_CNT": "70-74歲男性人口數",
    "A70A74_F_CNT": "70-74歲女性人口數",
    "A75A79_CNT": "75-79歲人口數",
    "A75A79_M_CNT": "75-79歲男性人口數",
    "A75A79_F_CNT": "75-79歲女性人口數",
    "A80A84_CNT": "80-84歲人口數",
    "A80A84_M_CNT": "80-84歲男性人口數",
    "A80A84_F_CNT": "80-84歲女性人口數",
    "A85A89_CNT": "85-89歲人口數",
    "A85A89_M_CNT": "85-89歲男性人口數",
    "A85A89_F_CNT": "85-89歲女性人口數",
    "A90A94_CNT": "90-94歲人口數",
    "A90A94_M_CNT": "90-94歲男性人口數",
    "A90A94_F_CNT": "90-94歲女性人口數",
    "A95A99_CNT": "95-99歲人口數",
    "A95A99_M_CNT": "95-99歲男性人口數",
    "A95A99_F_CNT": "95-99歲女性人口數",
    "A100UP_5_CNT": "100歲以上人口數",
    "A100UP_5_M_CNT": "100歲以上男性人口數",
    "A100UP_5_F_CNT": "100歲以上女性人口數",
    "INFO_TIME": "資料時間",
}

INDUSTRY_KEY_MAPPING = {
    "COUNTY_ID": "縣市代碼",
    "COUNTY": "縣市名稱",
    "TOWN_ID": "鄉鎮市區代碼",
    "TOWN": "鄉鎮市區名稱",
    "C_CNT": "工商業總家數",
    "C1_A_CNT": "農、林、漁、牧業",
    "C1_B_CNT": "礦業及土石採取業",
    "C1_C_CNT": "製造業",
    "C1_D_CNT": "電力及燃氣供應業",
    "C1_E_CNT": "用水供應及污染整治業",
    "C1_F_CNT": "營造業",
    "C1_G_CNT": "批發及零售業",
    "C1_H_CNT": "運輸及倉儲業",
    "C1_I_CNT": "住宿及餐飲業",
    "C1_J_CNT": "資訊及通訊傳播業",
    "C1_K_CNT": "金融及保險業",
    "C1_L_CNT": "不動產業",
    "C1_M_CNT": "專業、科學及技術服務業",
    "C1_N_CNT": "支援服務業",
    "C1_O_CNT": "公共行政及國防；強制性社會安全",
    "C1_P_CNT": "教育服務業",
    "C1_Q_CNT": "醫療保健及社會工作服務業",
    "C1_R_CNT": "藝術、娛樂及休閒服務業",
    "C1_S_CNT": "其他服務業",
    "INFO_TIME": "資料時間",
}

FISHING_KEY_MAPPING = {
    "COUNTY_ID": "縣市代碼",
    "COUNTY": "縣市名稱",
    "TOWN_ID": "鄉鎮市區代碼",
    "TOWN": "鄉鎮市區名稱",
    "COLUMN8": "人口數_合計",
    "COLUMN9": "人口數_遠洋漁業",
    "COLUMN10": "人口數_近海漁業",
    "COLUMN11": "人口數_沿海漁業",
    "COLUMN12": "人口數_海面養殖業",
    "COLUMN13": "人口數_內陸魚撈業",
    "COLUMN14": "人口數_內陸養殖業",
    "INFO_TIME": "資料時間",
}

POULTRY_KEY_MAPPING = {
    "COUNTY_ID": "縣市代碼",
    "COUNTY": "縣市名稱",
    "TOWN_ID": "鄉鎮市區代碼",
    "TOWN": "鄉鎮市區名稱",
    "COLUMN2": "蛋雞",
    "COLUMN3": "肉用雞",
    "COLUMN5": "蛋用鴨",
    "COLUMN6": "肉用鴨",
    "COLUMN7": "鵝",
    "COLUMN8": "火雞",
    "INFO_TIME": "資料時間",
}

LIVESTOCK_KEY_MAPPING = {
    "COUNTY_ID": "縣市代碼",
    "COUNTY": "縣市名稱",
    "TOWN_ID": "鄉鎮市區代碼",
    "TOWN": "鄉鎮市區名稱",
    "COLUMN1": "總計",
    "COLUMN2": "乳牛",
    "COLUMN3": "馬",
    "COLUMN4": "豬",
    "COLUMN5": "鹿",
    "COLUMN6": "兔",
    "COLUMN7": "羊",
    "INFO_TIME": "資料時間",
}


def send_soap_request(action, body):
    """發送 SOAP 請求"""
    soap_request = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                    xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
        <soap:Body>
            {body}
        </soap:Body>
    </soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": f"http://tempuri.org/{action}",
    }

    try:
        response = requests.post(URL, data=soap_request, headers=headers)
        response.raise_for_status()  # 如果請求失敗，會拋出 HTTPError
        return response.text
    except requests.RequestException as e:
        print(f"API 呼叫失敗：{e}")
        return None


def parse_soap_response(response_text, result_tag):
    """解析 SOAP 回應，提取 JSON 內容"""
    try:
        root = ET.fromstring(response_text)
        json_text = root.find(f".//{{http://tempuri.org/}}{result_tag}").text
        return json.loads(json_text)
    except (ET.ParseError, AttributeError, json.JSONDecodeError) as e:
        print(f"回應解析失敗：{e}")
        return None


def get_latest_time_list(level, query_type="summary"):
    """
    獲取最新的資料時間清單

    參數:
        level: "village" 表示村里, "town" 表示鄉鎮, "county" 表示縣市
        query_type: "summary" 表示人口統計, "index" 表示人口指標, "dynamics" 表示人口消長, "pyramid" 表示人口結構,
        "industry" 表示工商家數, "fishing" 表示漁戶統計, "livestock" 表示牲畜統計

    回傳:
        最新時間列表（格式為 113Y12M 或 113Y4S）
    """

    api_info = API_MAPPING[level]

    if query_type not in THEME_MAPPING:
        raise ValueError(
            "query_type 必須是 'summary','index','dynamics_index', 'structure' 或 'pyramid'"
        )

    meta_code = THEME_MAPPING[query_type]["meta_code"]

    body = f"""
    <GetSTTimeList xmlns="http://tempuri.org/">
        <oAPPId>{API_CONFIG["oAPPId"]}</oAPPId>
        <oAPIKey>{API_CONFIG["oAPIKey"]}</oAPIKey>
        <oResultDataType>{API_CONFIG["oResultDataType"]}</oResultDataType>
        <oSTUnitCode>{api_info['unit_code']}</oSTUnitCode>
        <oMetaDatCode>{meta_code}</oMetaDatCode>
    </GetSTTimeList>
    """
    response_text = send_soap_request("GetSTTimeList", body)
    if not response_text:
        return []

    json_data = parse_soap_response(response_text, "GetSTTimeListResult")
    if not json_data or "DateList" not in json_data:
        return []

    date_list = [item["INFO_TIME"] for item in json_data["DateList"]]

    time_dict = {}
    for date in date_list:
        date = date.replace("Y", " ").replace("M", "").replace("S", "")
        date_parts = date.split()

        if (
            query_type == "dynamics" or query_type == "dynamics_index"
        ):  # 只有人口消長是用季度計算
            if len(date_parts) == 2:
                year, quarter = map(int, date_parts)
            else:
                year = int(date_parts[0])
                quarter = 1  # 預設為第一季度
            time_dict[year] = max(time_dict.get(year, 0), quarter)
        elif query_type in [
            "fishing",
            "livestock",
            "farming",
            "poultry",
            "fruit",
            "crop",
            "special_crop",
            "rice",
            "vege",
        ]:  # 漁業、牲畜統計只用年份
            continue
        else:
            if len(date_parts) == 2:
                year, month = map(int, date_parts)
                time_dict[year] = max(time_dict.get(year, 0), month)

    if query_type == "dynamics" or query_type == "dynamics_index":
        return [f"{year}Y{quarter}S" for year, quarter in sorted(time_dict.items())]
    elif query_type in [
        "fishing",
        "livestock",
        "farming",
        "poultry",
        "fruit",
        "crop",
        "special_crop",
        "rice",
        "vege",
    ]:
        return sorted(date_list, key=lambda date: int(date.replace("Y", "")))
    else:
        return [
            f"{year}Y{str(month).zfill(2)}M"
            for year, month in sorted(time_dict.items())
        ]


def get_population_data(level, latest_dates, query_type="summary"):
    """
    查詢人口統計數據或人口統計指標

    參數:
        level: "county" 表示縣市
        latest_dates: 需要查詢的最新時間列表
        query_type: "summary" 表示人口統計, "index" 表示人口指標, "dynamics" 表示人口消長, "pyramid"表示人口結構
    """

    if not latest_dates:
        print("無可用的資料時間")
        return []

    api_info = API_MAPPING[level]

    if query_type not in THEME_MAPPING:
        raise ValueError("query_type 必須是 'summary','index','dynamics' 或 'pyramid'")

    selected_columns = THEME_MAPPING[query_type]["columns"].format(
        id_field=api_info["id_field"]
    )

    body = f"""
    <{api_info['api_name']} xmlns="http://tempuri.org/">
        <oAPPId>{API_CONFIG["oAPPId"]}</oAPPId>
        <oAPIKey>{API_CONFIG["oAPIKey"]}</oAPIKey>
        <oSTUnitCode>{api_info["unit_code"]}</oSTUnitCode>
        <oMetaDatCode>{THEME_MAPPING[query_type]['meta_code']}</oMetaDatCode>
        <oSelectColumns>{selected_columns}</oSelectColumns>
        <oFilterSTTimes>{','.join(latest_dates)}</oFilterSTTimes>
        <oFilterCountys>{QUERY_PARAMS["oFilterCountys"]}</oFilterCountys>
        {api_info["filter_town"]}
        {api_info["filter_village"]}
        <oResultDataType>{API_CONFIG["oResultDataType"]}</oResultDataType>
    </{api_info['api_name']}>
    """

    response_text = send_soap_request(api_info["api_name"], body)
    if not response_text:
        print("API 沒有回應任何內容")
        return []

    json_data = parse_soap_response(response_text, f"{api_info['api_name']}Result")
    if not json_data:
        print("API 回傳內容無法解析或格式錯誤")
        return []

    row_data = json_data.get("RowDataList", [])
    if not row_data:
        print("收到的 RowDataList 是空的")

    return row_data


def get_industry_data(level, latest_dates, query_type="summary"):
    """
    查詢人口統計數據或人口統計指標

    參數:
        latest_dates: 需要查詢的最新時間列表
        query_type: "summary" 表示工商家數, "fishing" 表示漁戶統計, "livestock" 表示牲畜統計
    """

    if not latest_dates:
        print("無可用的資料時間")
        return []

    level = "town"
    api_info = API_MAPPING[level]

    if query_type not in THEME_MAPPING:
        raise ValueError("query_type 必須是 'summary'")

    selected_columns = THEME_MAPPING[query_type]["columns"].format(
        id_field=api_info["id_field"]
    )

    body = f"""
    <{api_info['api_name']} xmlns="http://tempuri.org/">
        <oAPPId>{API_CONFIG["oAPPId"]}</oAPPId>
        <oAPIKey>{API_CONFIG["oAPIKey"]}</oAPIKey>
        <oSTUnitCode>{api_info["unit_code"]}</oSTUnitCode>
        <oMetaDatCode>{THEME_MAPPING[query_type]['meta_code']}</oMetaDatCode>
        <oSelectColumns>{selected_columns}</oSelectColumns>
        <oFilterSTTimes>{','.join(latest_dates)}</oFilterSTTimes>
        <oFilterCountys>{QUERY_PARAMS["oFilterCountys"]}</oFilterCountys>
        {api_info["filter_town"]}
        {api_info["filter_village"]}
        <oResultDataType>{API_CONFIG["oResultDataType"]}</oResultDataType>
    </{api_info['api_name']}>
    """

    response_text = send_soap_request(api_info["api_name"], body)
    if not response_text:
        return []

    json_data = parse_soap_response(response_text, f"{api_info['api_name']}Result")
    return json_data.get("RowDataList", [])


def convert_population_data(
    index_data, summary_data, dynamics_index_data, strcture_data, scale="village"
):

    # ---- helpers ----
    def minguo_to_ad(minguo_str: str) -> str:
        # '100Y12M' -> '2011'
        year_num = int(minguo_str.split("Y")[0])
        return str(year_num + 1911)

    def key_tuple(rec):
        """取 (民國年, V_ID) 做為 key，忽略月份"""
        info_time = rec.get("INFO_TIME")
        if info_time:
            year_part = info_time.split("Y")[0]  # 只取 Y 前面的數字
        else:
            year_part = None

        if scale == "village":
            return (year_part, rec.get("V_ID"))
        elif scale == "town":
            return (year_part, rec.get("TOWN_ID"))
        else:
            raise ValueError(f"Unsupported scale: {scale}")

    def get(d, key, default="-"):
        return default if d is None else (d.get(key, default))

    def as_str_or_dash(val):
        if val is None or val == "":
            return "-"
        return str(val)

    def as_float_str_or_dash(value, decimals=0):
        try:
            rounded_value = round(float(value), decimals)
            if decimals == 0:
                return str(int(rounded_value))
            return str(rounded_value)
        except (TypeError, ValueError):
            return "-"

    def to_float_or_none(val):
        try:
            # 避免把 '-' 之類的字元轉失敗
            if val is None or (isinstance(val, str) and val.strip() in {"", "-"}):
                return None
            return float(val)
        except Exception:
            return None

    # ---- build lookups ----
    idx = {key_tuple(r): r for r in (index_data or [])}
    summ = {key_tuple(r): r for r in (summary_data or [])}
    dyn = {key_tuple(r): r for r in (dynamics_index_data or [])}
    struc = {key_tuple(r): r for r in (strcture_data or [])}

    # 收集所有 (INFO_TIME, ID)
    all_keys = set()
    all_keys.update(idx.keys(), summ.keys(), dyn.keys(), struc.keys())

    grouped = defaultdict(list)

    for info_time, key in sorted(all_keys):
        if not info_time or not key:
            continue

        year = minguo_to_ad(info_time)

        rec_index = idx.get((info_time, key))
        rec_summary = summ.get((info_time, key))
        rec_dyn = dyn.get((info_time, key))
        rec_struc = struc.get((info_time, key))

        if scale == "village":
            v_id = key
            township_code = v_id
            county_code = 10007

            county_name = "彰化縣"
            township_name = "芳苑鄉"
            village_name = VILLAGE_NAME_MAPPING.get(v_id)

        elif scale == "town":
            town_id = key
            township_code = town_id
            county_code = 10007

            county_name = "彰化縣"
            township_name = TOWN_NAME_MAPPING.get(town_id)
            village_name = "-"  # 鄉鎮層級就不顯示村里

        # dynamics 加總：人口增加率 = 自然增加率 + 社會增加率（可得時）
        nat_inc = to_float_or_none(get(rec_dyn, "NATURE_INC_PER"))
        soc_inc = to_float_or_none(get(rec_dyn, "SOCIAL_INC_PER"))
        if nat_inc is not None and soc_inc is not None:
            pop_inc_rate = str(nat_inc + soc_inc)
        else:
            pop_inc_rate = "-"

        item = {
            "縣市代碼": as_str_or_dash(county_code),
            "縣市名稱": as_str_or_dash(county_name),
            "鄉鎮市區代碼": as_str_or_dash(township_code),
            "鄉鎮市區名稱": as_str_or_dash(township_name),
            "村里代碼": as_str_or_dash(v_id if scale == "village" else "-"),
            "村里名稱": as_str_or_dash(village_name if scale == "village" else "-"),
            # summary
            "戶數": as_float_str_or_dash(get(rec_summary, "H_CNT"), decimals=0),
            "人口數": as_float_str_or_dash(get(rec_summary, "P_CNT"), decimals=0),
            # index
            "人口密度": as_float_str_or_dash(get(rec_index, "P_DEN"), decimals=2),
            "性別比": as_float_str_or_dash(get(rec_index, "M_F_RAT"), decimals=2),
            "扶養比": as_float_str_or_dash(
                get(rec_index, "DEPENDENCY_RAT"), decimals=2
            ),
            "扶幼比": as_float_str_or_dash(
                get(rec_index, "A0A14_A15A65_RAT"), decimals=2
            ),
            "扶老比": as_float_str_or_dash(
                get(rec_index, "A65UP_A15A64_RAT"), decimals=2
            ),
            "老化指數": as_float_str_or_dash(
                get(rec_index, "A65_A0A14_RAT"), decimals=2
            ),
            # dynamics
            "粗出生率": as_float_str_or_dash(get(rec_dyn, "BORN_PER"), decimals=2),
            "粗死亡率": as_float_str_or_dash(get(rec_dyn, "DEAD_PER"), decimals=2),
            "自然增加率": as_float_str_or_dash(
                get(rec_dyn, "NATURE_INC_PER"), decimals=2
            ),
            "社會增加率": as_float_str_or_dash(
                get(rec_dyn, "SOCIAL_INC_PER"), decimals=2
            ),
            "人口增加率": as_float_str_or_dash(pop_inc_rate, decimals=2),
            # structure
            "0-14歲人口數": as_float_str_or_dash(
                get(rec_struc, "A0A14_CNT"), decimals=0
            ),
            "15-64歲人口數": as_float_str_or_dash(
                get(rec_struc, "A15A64_CNT"), decimals=0
            ),
            "65歲以上人口數": as_float_str_or_dash(
                get(rec_struc, "A65UP_CNT"), decimals=0
            ),
            "資料時間": f"{info_time}Y",
        }

        grouped[year].append(item)

    # 排序輸出
    result = [{"year": y, "data": grouped[y]} for y in sorted(grouped.keys())]
    return result


def covert_pyrimad_data(data):
    """將 list 中的每個 dict key 依照 mapping 轉換"""

    def as_float_str_or_dash(value, decimals=0):
        try:
            rounded_value = round(float(value), decimals)
            if decimals == 0:
                return str(int(rounded_value))
            return str(rounded_value)
        except (TypeError, ValueError):
            return "-"

    skip_keys = {
        "縣市代碼",
        "縣市名稱",
        "鄉鎮市區代碼",
        "鄉鎮市區名稱",
        "村里代碼",
        "村里名稱",
        "資料時間",
    }
    grouped = {}

    for item in data:
        new_item = {}
        for key, value in item.items():
            new_key = PYRIMAD_KEY_MAPIING.get(key, key)
            if new_key not in skip_keys:
                new_item[new_key] = as_float_str_or_dash(value, decimals=0)
            else:
                new_item[new_key] = value

        # 取得西元年
        info_time = item.get("INFO_TIME") or item.get("資料時間")
        if info_time:
            year = str(int(info_time.split("Y")[0]) + 1911)
        else:
            year = "-"

        grouped.setdefault(year, []).append(new_item)

    return [{"year": year, "data": rows} for year, rows in grouped.items()]


def convert_industry_map_data(
    farming_data,
    fishing_data,
    poultry_data,
    fruit_data,
    crop_data,
    special_crop_data,
    rice_data,
    livestock_data,
    vege_data,
    industry_data,
):

    # ---- helpers ----
    def minguo_to_ad(minguo_str: str) -> str:
        # '100Y12M' -> '2011'
        year_num = int(minguo_str.split("Y")[0])
        return str(year_num + 1911)

    def key_tuple(rec):
        """取 (民國年, V_ID) 做為 key，忽略月份"""
        info_time = rec.get("INFO_TIME")
        if info_time:
            year_part = info_time.split("Y")[0]  # 只取 Y 前面的數字
        else:
            year_part = None

        return (year_part, rec.get("TOWN_ID"))

    def get(d, key, default="-"):
        return default if d is None else (d.get(key, default))

    def as_str_or_dash(val):
        if val is None or val == "":
            return "-"
        return str(val)

    def as_float_str_or_dash(value, decimals=0):
        try:
            rounded_value = round(float(value), decimals)
            if decimals == 0:
                return str(int(rounded_value))
            return str(rounded_value)
        except (TypeError, ValueError):
            return "-"

    def to_float_or_zero(val):
        try:
            if val is None or (isinstance(val, str) and val.strip() == ""):
                return 0.0
            return float(val)
        except Exception:
            return 0.0

    # ---- build lookups ----
    farming = {key_tuple(r): r for r in (farming_data or [])}
    fishing = {key_tuple(r): r for r in (fishing_data or [])}
    poultry = {key_tuple(r): r for r in (poultry_data or [])}
    fruit = {key_tuple(r): r for r in (fruit_data or [])}
    crop = {key_tuple(r): r for r in (crop_data or [])}
    special_crop = {key_tuple(r): r for r in (special_crop_data or [])}
    rice = {key_tuple(r): r for r in (rice_data or [])}
    livestock = {key_tuple(r): r for r in (livestock_data or [])}
    vege = {key_tuple(r): r for r in (vege_data or [])}
    industry = {key_tuple(r): r for r in (industry_data or [])}

    # 收集所有 (INFO_TIME, ID)
    all_keys = set()
    all_keys.update(
        farming.keys(),
        fishing.keys(),
        poultry.keys(),
        fruit.keys(),
        crop.keys(),
        special_crop.keys(),
        rice.keys(),
        livestock.keys(),
        vege.keys(),
        industry.keys(),
    )

    grouped = defaultdict(list)

    for info_time, key in sorted(all_keys):
        if not info_time or not key:
            continue

        year = minguo_to_ad(info_time)

        rec_farming = farming.get((info_time, key))
        rec_fishing = fishing.get((info_time, key))
        rec_poultry = poultry.get((info_time, key))
        rec_fruit = fruit.get((info_time, key))
        rec_crop = crop.get((info_time, key))
        rec_special_crop = special_crop.get((info_time, key))
        rec_rice = rice.get((info_time, key))
        rec_livestock = livestock.get((info_time, key))
        rec_vege = vege.get((info_time, key))
        rec_industry = industry.get((info_time, key))

        town_id = key
        township_code = town_id
        county_code = 10007

        county_name = "彰化縣"
        township_name = TOWN_NAME_MAPPING.get(town_id)

        fruit_count = to_float_or_zero(get(rec_fruit, "COLUMN2"))
        crop_count = to_float_or_zero(get(rec_crop, "COLUMN2"))
        special_crop_count = to_float_or_zero(get(rec_special_crop, "COLUMN2"))
        rice_count = to_float_or_zero(get(rec_rice, "COLUMN2"))
        vege_count = to_float_or_zero(get(rec_vege, "COLUMN2"))

        farming_count = str(
            fruit_count + crop_count + special_crop_count + rice_count + vege_count
        )

        fruit_area = to_float_or_zero(get(rec_fruit, "COLUMN1"))
        crop_area = to_float_or_zero(get(rec_crop, "COLUMN1"))
        special_crop_area = to_float_or_zero(get(rec_special_crop, "COLUMN1"))
        rice_area = to_float_or_zero(get(rec_rice, "COLUMN1"))
        vege_area = to_float_or_zero(get(rec_vege, "COLUMN1"))

        farming_area = str(
            fruit_area + crop_area + special_crop_area + rice_area + vege_area
        )

        poultry_COLUMN2 = to_float_or_zero(get(rec_poultry, "COLUMN2"))
        poultry_COLUMN3 = to_float_or_zero(get(rec_poultry, "COLUMN3"))
        poultry_COLUMN5 = to_float_or_zero(get(rec_poultry, "COLUMN5"))
        poultry_COLUMN6 = to_float_or_zero(get(rec_poultry, "COLUMN6"))
        poultry_COLUMN7 = to_float_or_zero(get(rec_poultry, "COLUMN7"))
        poultry_COLUMN8 = to_float_or_zero(get(rec_poultry, "COLUMN8"))

        poultry_count = str(
            poultry_COLUMN2
            + poultry_COLUMN3
            + poultry_COLUMN5
            + poultry_COLUMN6
            + poultry_COLUMN7
            + poultry_COLUMN8
        )

        item = {
            "縣市代碼": as_str_or_dash(county_code),
            "縣市名稱": as_str_or_dash(county_name),
            "鄉鎮市區代碼": as_str_or_dash(township_code),
            "鄉鎮市區名稱": as_str_or_dash(township_name),
            "農耕土地總計(公頃)": as_float_str_or_dash(
                get(rec_farming, "COLUMN1"), decimals=2
            ),
            "漁戶人口數(遠洋、近海、沿海、海面養殖、內陸漁撈、內陸養殖)": as_float_str_or_dash(
                get(rec_fishing, "COLUMN8"), decimals=0
            ),
            "家畜數(牛、馬、豬、鹿、兔、羊)-頭": as_float_str_or_dash(
                get(rec_livestock, "COLUMN1"), decimals=0
            ),
            "農產產量總計(公噸)": as_float_str_or_dash(farming_count, decimals=2),
            "農產收穫面積總計(公頃)": as_float_str_or_dash(farming_area, decimals=2),
            "家禽數(蛋雞、肉雞、蛋鴨、肉鴨、鵝、火雞)-千隻": as_float_str_or_dash(
                poultry_count, decimals=2
            ),
            "工商業總家數": as_float_str_or_dash(
                get(rec_industry, "C_CNT"), decimals=0
            ),
        }

        grouped[year].append(item)

    # 排序輸出
    result = [{"year": y, "data": grouped[y]} for y in sorted(grouped.keys())]
    return result


def convert_to_dict_format_data(data, mapping):
    """將 list 中的每個 dict key 依照 mapping 轉換"""

    def as_float_str_or_dash(value, decimals=0):
        try:
            rounded_value = round(float(value), decimals)
            if decimals == 0:
                return str(int(rounded_value))
            return str(rounded_value)
        except (TypeError, ValueError):
            return "-"

    skip_keys = {
        "縣市代碼",
        "縣市名稱",
        "鄉鎮市區代碼",
        "鄉鎮市區名稱",
        "資料時間",
    }
    grouped = {}

    for item in data:
        new_item = {}
        for key, value in item.items():
            new_key = mapping.get(key, key)
            if new_key not in skip_keys:
                new_item[new_key] = as_float_str_or_dash(value, decimals=0)
            else:
                new_item[new_key] = value

        # 取得西元年
        info_time = item.get("INFO_TIME") or item.get("資料時間")
        if info_time:
            year = str(int(info_time.split("Y")[0]) + 1911)
        else:
            year = "-"

        grouped.setdefault(year, []).append(new_item)

    return [{"year": year, "data": rows} for year, rows in grouped.items()]


def convert_agriculture_data(
    farming_data,
    fruit_data,
    crop_data,
    special_crop_data,
    rice_data,
    vege_data,
):

    # ---- helpers ----
    def minguo_to_ad(minguo_str: str) -> str:
        # '100Y12M' -> '2011'
        year_num = int(minguo_str.split("Y")[0])
        return str(year_num + 1911)

    def key_tuple(rec):
        """取 (民國年, V_ID) 做為 key，忽略月份"""
        info_time = rec.get("INFO_TIME")
        if info_time:
            year_part = info_time.split("Y")[0]  # 只取 Y 前面的數字
        else:
            year_part = None

        return (year_part, rec.get("TOWN_ID"))

    def get(d, key, default="-"):
        return default if d is None else (d.get(key, default))

    def as_str_or_dash(val):
        if val is None or val == "":
            return "-"
        return str(val)

    def as_float_str_or_dash(value, decimals=0):
        try:
            rounded_value = round(float(value), decimals)
            if decimals == 0:
                return str(int(rounded_value))
            return str(rounded_value)
        except (TypeError, ValueError):
            return "-"

    def to_float_or_zero(val):
        try:
            if val is None or (isinstance(val, str) and val.strip() == ""):
                return 0.0
            return float(val)
        except Exception:
            return 0.0

    # ---- build lookups ----
    fruit = {key_tuple(r): r for r in (fruit_data or [])}
    crop = {key_tuple(r): r for r in (crop_data or [])}
    special_crop = {key_tuple(r): r for r in (special_crop_data or [])}
    rice = {key_tuple(r): r for r in (rice_data or [])}
    vege = {key_tuple(r): r for r in (vege_data or [])}
    farming = {key_tuple(r): r for r in (farming_data or [])}

    # 收集所有 (INFO_TIME, ID)
    all_keys = set()
    all_keys.update(
        fruit.keys(),
        crop.keys(),
        special_crop.keys(),
        rice.keys(),
        vege.keys(),
        farming.keys(),
    )

    grouped = defaultdict(list)

    for info_time, key in sorted(all_keys):
        if not info_time or not key:
            continue

        year = minguo_to_ad(info_time)

        rec_fruit = fruit.get((info_time, key))
        rec_crop = crop.get((info_time, key))
        rec_special_crop = special_crop.get((info_time, key))
        rec_rice = rice.get((info_time, key))
        rec_vege = vege.get((info_time, key))
        rec_farming = farming.get((info_time, key))

        town_id = key
        township_code = town_id
        county_code = 10007

        county_name = "彰化縣"
        township_name = TOWN_NAME_MAPPING.get(town_id)

        fruit_count = to_float_or_zero(get(rec_fruit, "COLUMN2"))
        crop_count = to_float_or_zero(get(rec_crop, "COLUMN2"))
        special_crop_count = to_float_or_zero(get(rec_special_crop, "COLUMN2"))
        rice_count = to_float_or_zero(get(rec_rice, "COLUMN2"))
        vege_count = to_float_or_zero(get(rec_vege, "COLUMN2"))

        farming_count = str(
            fruit_count + crop_count + special_crop_count + rice_count + vege_count
        )

        fruit_area = to_float_or_zero(get(rec_fruit, "COLUMN1"))
        crop_area = to_float_or_zero(get(rec_crop, "COLUMN1"))
        special_crop_area = to_float_or_zero(get(rec_special_crop, "COLUMN1"))
        rice_area = to_float_or_zero(get(rec_rice, "COLUMN1"))
        vege_area = to_float_or_zero(get(rec_vege, "COLUMN1"))

        farming_area = str(
            fruit_area + crop_area + special_crop_area + rice_area + vege_area
        )

        item = {
            "縣市代碼": as_str_or_dash(county_code),
            "縣市名稱": as_str_or_dash(county_name),
            "鄉鎮市區代碼": as_str_or_dash(township_code),
            "鄉鎮市區名稱": as_str_or_dash(township_name),
            "果品總計_收穫面積": as_float_str_or_dash(
                get(rec_fruit, "COLUMN1"), decimals=2
            ),
            "果品總計_產量": as_float_str_or_dash(
                get(rec_fruit, "COLUMN2"), decimals=0
            ),
            "特用作物總計_收穫面積": as_float_str_or_dash(
                get(rec_special_crop, "COLUMN1"), decimals=2
            ),
            "特用作物總計_產量": as_float_str_or_dash(
                get(rec_special_crop, "COLUMN2"), decimals=0
            ),
            "稻米合計_收穫面積": as_float_str_or_dash(
                get(rec_rice, "COLUMN1"), decimals=2
            ),
            "稻米合計_產量": as_float_str_or_dash(get(rec_rice, "COLUMN2"), decimals=0),
            "蔬菜總計_收穫面積": as_float_str_or_dash(
                get(rec_vege, "COLUMN1"), decimals=2
            ),
            "蔬菜總計_產量": as_float_str_or_dash(get(rec_vege, "COLUMN2"), decimals=0),
            "雜糧總計_收穫面積": as_float_str_or_dash(
                get(rec_crop, "COLUMN1"), decimals=2
            ),
            "雜糧總計_產量": as_float_str_or_dash(get(rec_crop, "COLUMN2"), decimals=0),
            "總收穫面積": as_float_str_or_dash(farming_area, decimals=2),
            "總產量": as_float_str_or_dash(farming_count, decimals=0),
            "耕作地/合計": as_float_str_or_dash(
                get(rec_farming, "COLUMN2"), decimals=2
            ),
            "長期休閒地": as_float_str_or_dash(get(rec_farming, "COLUMN5"), decimals=2),
            "農耕土地總計": as_float_str_or_dash(
                get(rec_farming, "COLUMN1"), decimals=2
            ),
        }

        grouped[year].append(item)

    # 排序輸出
    result = [{"year": y, "data": grouped[y]} for y in sorted(grouped.keys())]
    return result
