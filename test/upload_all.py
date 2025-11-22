import os
import requests

def upload_file(file_path, url):
    # 打开文件
    with open(file_path, 'rb') as file:
        files = {'file': file}
        # 发送POST请求上传文件
        response = requests.post(url, files=files)
        # 返回响应结果
        return response.json()

# 指定文件夹路径
folder_path = '/home/nameless0078/rag/dataset_txt'
# 指定上传接口的URL
url = 'http://localhost:5000/upload'

# 递归遍历文件夹及其子文件夹下的所有文件
for root, dirs, files in os.walk(folder_path):
    for filename in files:
        # 构建文件的完整路径
        file_path = os.path.join(root, filename)
        # 上传文件并打印响应结果
        print(f'正在上传文件：{file_path}')
        response = upload_file(file_path, url)
        print(f'文件 {filename} 上传结果：{response}')