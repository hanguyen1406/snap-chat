import requests,time

token = 'k1oi6SnuhANmMsHhrsrv5trLxTrCnExzLWlpuRun2dD2jinDOk3FxZSFjGSWsl7s'

url = "https://vannhimailtest.click/api/v1/createEmail"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# JSON hợp lệ (không có dấu //)
data = {
    "name": "test",
    "domain": "vannhimailtest.click"
}

response = requests.post(url, json=data, headers=headers)

print("Status:", response.status_code)
print("Raw response:", response.text)

try:
    print("JSON:", response.json())
except:
    print("❌ Server không trả JSON")



headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

data = {
    "email": "test@vannhimailtest.click"
}
for i in range(300):

    response = requests.get(
        'https://vannhimailtest.click/api/v1/mails',
        headers=headers,
        params=data  # <-- quan trọng
    )

    print("Status:", response.status_code)
    print("Raw response:", response.text)

    try:
        print("JSON:", response.json())
    except:
        print("❌ Server không trả JSON")

    # time.sleep(10)