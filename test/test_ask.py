import requests

url = 'http://localhost:5000/ask'
data = {
    'query': '文化数字化的课题二是什么？'
}

response = requests.post(url, json=data)
return_str=response.json()
print('answer:',return_str['answer'])
print('retrieved_result:',return_str['retrieved_result'])
# print(response.json())