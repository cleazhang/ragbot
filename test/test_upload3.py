import requests

# 文件上传的 URL
url = 'http://localhost:5000/upload'

# 要上传的文件列表
files_to_upload = [
    ('file', ('file1.txt', open('/home/nameless0078/rag/dataset/web_crawler/常见问题/何时公布“家庭积分”？如何查询“家庭积分”.txt', 'rb'))),
    ('file', ('file2.txt', open('/home/nameless0078/rag/dataset/web_crawler/常见问题/家庭亲属关系核验未通过的，能否继续参加指标配置.txt', 'rb'))),
    # 可以继续添加更多的文件
]

# 发送 POST 请求
response = requests.post(url, files=files_to_upload)

# 确保所有文件都已关闭，避免资源泄露
for _, (_, file) in files_to_upload:
    file.close()

# 检查响应并打印
if response.ok:
    print('Files uploaded successfully!')
    print(response.json())  # 打印服务器的响应内容（假设响应是 JSON 格式）
else:
    print('Failed to upload files')
    print(response.text)