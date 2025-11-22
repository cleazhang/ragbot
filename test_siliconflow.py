#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试硅基流动API连接
使用方法: python test_siliconflow.py
"""

import os
import sys

# 添加flask_app到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'flask_app'))

# 设置环境变量（请替换为你的实际API密钥）
os.environ['USE_SILICONFLOW'] = 'true'
os.environ['SILICONFLOW_API_KEY'] = 'sk-ziyyhopxmxuffgjgwphatkqjxftfenxvmlhpcycnzisdxyrr'
os.environ['SILICONFLOW_MODEL'] = 'Qwen/QwQ-32B'

try:
    from app.llm_models import get_llm
    
    print("=" * 50)
    print("测试硅基流动API连接")
    print("=" * 50)
    
    # 获取LLM实例
    llm = get_llm()
    print(f"✅ 成功创建LLM实例: {llm._llm_type}")
    
    # 测试调用
    print("\n发送测试问题...")
    test_prompt = "你好，请简单介绍一下你自己。"
    response = llm._call(test_prompt)
    
    print("\n" + "=" * 50)
    print("API响应:")
    print("=" * 50)
    print(response)
    print("=" * 50)
    print("\n✅ 测试成功！硅基流动API工作正常。")
    
except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    print("\n请检查:")
    print("1. API密钥是否正确")
    print("2. 网络连接是否正常")
    print("3. 环境变量是否设置正确")
    import traceback
    traceback.print_exc()

