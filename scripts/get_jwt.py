import base64

import requests

url = "http://localhost:9000/oauth/token/"

# local
client_id = "Rh3MxlmC0oDwSqhowGoiAg7UJIpl8t9ZDUbgVtoc"
client_secret = "2vCSqgmorZOPFUgeDJr0dd5IBmDlVMldbRJUCOGpg2bifLGdZZUlI8n7k6y6pQLNIleILMn8a80IuJHic0UJQiKRFNqHgLzP0z3KjotZeptXk21wFmY6v4KpBkUoivk7"

auth_value = f"{client_id}:{client_secret}"
auth_value_bytes = auth_value.encode("ascii")
auth_value_b64 = base64.b64encode(auth_value_bytes).decode("ascii")

data = {
    "grant_type": "client_credentials",
    "scope": "blender.read blender.write",
    "audience": "blender.utm.dev.airoplatform.com",
    "client_uuid": "e28163ce-b86d-4145-8df3-c8dad2e0b601",
}

headers = {"Authorization": f"Basic {auth_value_b64}", "Content-Type": "application/x-www-form-urlencoded"}

response = requests.post(url, data=data, headers=headers)

print(response.status_code)
print(response.json())
