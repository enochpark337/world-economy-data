import requests

# 1. BASE URL (World Bank API 공통 주소)
BASE_URL = "https://api.worldbank.org/v2"

# 2. 우리가 사용할 값들
country = "KOR"
indicator = "NY.GDP.MKTP.CD"  # GDP (current US$)

# 3. endpoint 조립
endpoint = f"/country/{country}/indicator/{indicator}"

# 4. 최종 URL
url = BASE_URL + endpoint

# 5. query parameters
params = {
    "format": "json"
}

print("Request URL:", url)

# 6. API 호출
response = requests.get(url, params=params)

# 7. 응답 상태 코드 확인
print("Status Code:", response.status_code)

data = response.json()

print("Response type:", type(data))
print("Top-level length:", len(data))

meta = data[0]
rows = data[1]

print("Metadata:", meta)
print("First data row:", rows[0])