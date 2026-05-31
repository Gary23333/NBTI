#!/usr/bin/env python3
"""测试预加载策略"""

import requests
import time
import json

BASE_URL = "http://localhost:8080/api"

def test_preload_flow():
    """测试预加载流程"""
    print("=" * 60)
    print("开始测试预加载流程")
    print("=" * 60)
    
    # 1. 开始测试
    print("\n[步骤 1] 开始测试")
    response = requests.post(f"{BASE_URL}/chat", json={
        "message": "开始测试",
        "conversation_id": ""
    })
    data = response.json()
    conversation_id = data.get("conversation_id")
    print(f"  conversation_id: {conversation_id}")
    print(f"  answer: {data.get('answer', '')[:100]}...")
    
    # 等待一下，查看日志
    time.sleep(2)
    
    # 2. 模拟预加载（用户选择选项 A）
    print("\n[步骤 2] 模拟预加载选项 A")
    response = requests.post(f"{BASE_URL}/chat/preload", json={
        "message": "选项A的内容",
        "conversation_id": conversation_id
    })
    print(f"  preload response: {response.status_code}")
    
    # 3. 模拟预加载（用户选择选项 B）
    print("\n[步骤 3] 模拟预加载选项 B")
    response = requests.post(f"{BASE_URL}/chat/preload", json={
        "message": "选项B的内容",
        "conversation_id": conversation_id
    })
    print(f"  preload response: {response.status_code}")
    
    # 等待一下，查看日志
    time.sleep(2)
    
    # 4. 用户实际作答（选择选项 A）
    print("\n[步骤 4] 用户实际作答（选择选项 A）")
    response = requests.post(f"{BASE_URL}/chat", json={
        "message": "选项A的内容",
        "conversation_id": conversation_id
    })
    data = response.json()
    print(f"  answer: {data.get('answer', '')[:100]}...")
    
    # 等待一下，查看日志
    time.sleep(2)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_preload_flow()
