import requests
import json

# Test d'ajout de contrainte sur E-G
url = "http://127.0.0.1:5000/graph/edge/constraint"
data = {
    "u": "E",
    "v": "G",
    "contrainte": 5.0
}

try:
    response = requests.put(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Erreur: {e}")
