from django.test import TestCase

# Create your tests here.
import requests

response = requests.get('http://localhost:8000/products/')  # change URL to match your endpoint
if response.status_code == 200:
    products = response.json()
    print(products)
else:
    print("Error:", response.status_code)
