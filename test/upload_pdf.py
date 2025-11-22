import requests

url = 'http://localhost:5000/upload'
files = {'file': open("/home/nameless0078/rag/文化数字化项目任务书.pdf", 'rb')}

response = requests.post(url, files=files)
print(response.json())