import pycountry
from typing import List, Dict

OECD_MEMBERS = [
    "Australia","Austria","Belgium","Canada","Chile","Colombia","Costa Rica","Czechia",
    "Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Iceland",
    "Ireland","Israel","Italy","Japan","Korea","Latvia","Lithuania","Luxembourg",
    "Mexico","Netherlands","New Zealand","Norway","Poland","Portugal","Slovak Republic",
    "Slovenia","Spain","Sweden","Switzerland","Türkiye","United Kingdom","United States"
]

# 🔑 수동 매핑 테이블 (실무 필수)
MANUAL_ISO3 = {
    "Korea": "KOR",
    "United States": "USA",
    "United Kingdom": "GBR",
    "Türkiye": "TUR",
    "Turkey": "TUR",
    "Slovak Republic": "SVK",
    "Czechia": "CZE",
}

def name_to_iso3(name: str) -> str:
    # 1️⃣ 수동 매핑 먼저
    if name in MANUAL_ISO3:
        return MANUAL_ISO3[name]

    # 2️⃣ pycountry 자동 검색
    try:
        country = pycountry.countries.search_fuzzy(name)[0]
        return country.alpha_3
    except LookupError:
        raise ValueError(f"ISO3 conversion failed for country name: {name}")


def get_oecd_countries_iso3() -> List[Dict[str, str]]:
    """
    Returns a list like:
    [{"name": "Korea", "iso3": "KOR"}, ...]
    """
    out: List[Dict[str, str]] = []
    for name in OECD_MEMBERS:
        out.append({"name": name, "iso3": name_to_iso3(name)})
    return out

if __name__ == "__main__":
    # Only runs when you execute this file directly, not when importing.
    print(get_oecd_countries_iso3())