import requests
import uuid
import json

url = "http://localhost:8000/api/chat"
headers = {"Content-Type": "application/json"}
data = {
    "message": "I am Pratik and looking for life insurance.",
    "thread_id": str(uuid.uuid4())
}

try:
    print("Sending request to:", url)
    response = requests.post(url, headers=headers, json=data)
    print("Status Code:", response.status_code)
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
