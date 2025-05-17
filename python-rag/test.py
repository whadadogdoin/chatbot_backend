import requests
import json

API_URL = "https://api.jina.ai/v1/embeddings"
API_KEY = "jina_a1256721fe6440c983873b32f89c6018PZUINVebRcyEUKrNO3Z9a-LidRZP"

data = {
    "model": "jina-clip-v2",
    "input": [{"text": "Hello world"}]
}
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(API_URL, headers=headers, data=json.dumps(data))
print("Status code:", response.status_code)
print("Response JSON:", response.json())