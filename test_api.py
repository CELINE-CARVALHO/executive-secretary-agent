import requests
import json

url = "http://127.0.0.1:5000/api/process-email"

payload = {
    "sender": "ceo@company.com",
    "subject": "Team meeting",
    "body": "Please schedule a team meeting tomorrow at 10am and remind me 30 minutes before."
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=payload)

print("Status Code:", response.status_code)
print("Raw Response Text:")
print(response.text)

# Try JSON only if possible
try:
    print("Parsed JSON:")
    print(response.json())
except Exception:
    print("Response was not JSON")
