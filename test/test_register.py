import requests

url = 'http://localhost:8089/register'
data = {
    'username': 'newuser2',
    'password': 'newpassword1'
}

response = requests.post(url, data=data)
print(response.status_code)
print(response.text)