import re
from data.importing.adapters.waterquality import WaterQualityAdapter
from data.importing.adapters.sediment import SedimentAdapter
from data.importing.adapters.crab import CrabAdapter

ADAPTERS = {
    "fy_wq": WaterQualityAdapter,
    "fy_sediment": SedimentAdapter,
    "fy_crab": CrabAdapter,
}


def normalize_package_name(package_name):
    return re.sub(r"-\d{6}$", "", package_name)
