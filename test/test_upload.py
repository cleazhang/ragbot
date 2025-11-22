import requests

url = 'http://localhost:5000/upload'
files = {'file': open("/home/nameless0078/rag/申请小客车指标办事说明（单位）.html", 'rb')}

response = requests.post(url, files=files)
print(response.json())