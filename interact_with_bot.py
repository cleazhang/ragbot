#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
与RAG Bot交互的完整示例脚本
使用方法: python interact_with_bot.py
"""

import requests
import json

# 配置
BASE_URL = "http://127.0.0.1:5050"
USERNAME = "demo_user"
PASSWORD = "demo_pass123"

def register_user():
    """注册新用户"""
    print("=" * 50)
    print("1. 注册用户")
    print("=" * 50)
    resp = requests.post(f"{BASE_URL}/register", data={
        'username': USERNAME,
        'password': PASSWORD
    })
    if resp.status_code == 201:
        print(f"✅ 注册成功: {USERNAME}")
        return True
    elif resp.status_code == 400:
        print(f"ℹ️  用户已存在: {USERNAME}")
        return True
    else:
        print(f"❌ 注册失败: {resp.status_code} - {resp.text}")
        return False

def login():
    """登录"""
    print("\n" + "=" * 50)
    print("2. 用户登录")
    print("=" * 50)
    resp = requests.post(f"{BASE_URL}/login", data={
        'username': USERNAME,
        'password': PASSWORD
    })
    if resp.status_code == 200:
        print(f"✅ 登录成功")
        return resp.cookies
    else:
        print(f"❌ 登录失败: {resp.status_code} - {resp.text}")
        return None

def upload_file(session, file_path):
    """上传文件"""
    print("\n" + "=" * 50)
    print(f"3. 上传文件: {file_path}")
    print("=" * 50)
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            resp = session.post(f"{BASE_URL}/upload", files=files)
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ 上传成功")
            print(f"   文件路径: {result.get('files', [])}")
            return True
        else:
            print(f"❌ 上传失败: {resp.status_code} - {resp.text[:200]}")
            return False
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        return False

def ask_question(session, question):
    """向Bot提问"""
    print("\n" + "=" * 50)
    print(f"4. 提问: {question}")
    print("=" * 50)
    resp = session.post(f"{BASE_URL}/ask", data={'query': question})
    if resp.status_code == 200:
        result = resp.json()
        print(f"✅ Bot回答:")
        print(f"   {result.get('answer', '无回答')}")
        print(f"\n📄 检索到的文档片段:")
        for i, doc in enumerate(result.get('retrieved_result', [])[:3], 1):
            print(f"   [{i}] {doc[:100]}...")
        return result
    else:
        print(f"❌ 提问失败: {resp.status_code} - {resp.text[:200]}")
        return None

def clear_history(session):
    """清除历史记录"""
    print("\n" + "=" * 50)
    print("5. 清除历史记录")
    print("=" * 50)
    resp = session.post(f"{BASE_URL}/clear_history")
    if resp.status_code == 200:
        print("✅ 历史记录已清除")
    else:
        print(f"❌ 清除失败: {resp.status_code}")

def main():
    """主函数 - 完整的交互流程"""
    print("\n" + "🤖" * 25)
    print("RAG Bot 交互示例")
    print("🤖" * 25)
    
    # 1. 注册
    if not register_user():
        return
    
    # 2. 登录并创建会话
    cookies = login()
    if not cookies:
        return
    
    session = requests.Session()
    session.cookies.update(cookies)
    
    # 3. 上传文件（使用README.md作为示例）
    import os
    readme_path = os.path.join(os.path.dirname(__file__), "1.txt")
    if os.path.exists(readme_path):
        upload_file(session, readme_path)
    else:
        print(f"\n⚠️  1.txt 不存在，跳过上传步骤")
        print("   你可以手动上传文件，或创建测试文件")
    
    # 4. 提问示例
    questions = [
        "如何实现耕地资源的可持续发展？",
        "项目区位于什么位置？"
    ]
    
    for q in questions:
        ask_question(session, q)
        print("\n" + "-" * 50)
    
    # 5. 清除历史（可选）
    # clear_history(session)
    
    print("\n" + "=" * 50)
    print("✅ 交互完成！")
    print("=" * 50)
    print("\n💡 提示:")
    print("   - 你可以修改脚本中的问题继续提问")
    print("   - 上传更多文件后，Bot可以回答更多问题")
    print("   - 使用 clear_history() 可以清除对话历史")

if __name__ == "__main__":
    main()

