import requests

url = 'http://10.112.208.173:8089/login'
data = {
    'username': 'newuser2',
    'password': 'newpassword1'
}

response = requests.post(url, data=data)
print(response.status_code)
print(response.text)