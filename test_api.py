import requests
import json

url = "http://localhost:8000/api/chat"
headers = {"Content-Type": "application/json"}
data = {"message": "I am looking for life insurance."}

try:
    print("Sending request to:", url)
    response = requests.post(url, headers=headers, json=data)
    print("Status Code:", response.status_code)
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
