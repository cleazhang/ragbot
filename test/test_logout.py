import requests

url = 'http://localhost:5000/logout'

response = requests.get(url)
print(response.status_code)
print(response.text)