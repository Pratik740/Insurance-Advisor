import requests
import json

url = "http://localhost:8000/api/chat"
headers = {"Content-Type": "application/json"}
data = {
    "message": "Just tell me all the information about me that I have provided to u",
    "thread_id": "pratik-session-4" 
}

try:
    print("Sending request to:", url)
    response = requests.post(url, headers=headers, json=data)
    print("Status Code:", response.status_code)
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
