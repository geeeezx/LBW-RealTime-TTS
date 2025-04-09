import requests
import json
import time
import os
import sys

# 测试非流式API
def test_normal_api():
    print("正在测试非流式API...")
    response = requests.post(
        "http://localhost:8000/api/chat",
        json={
            "prompt": "你是谁？请简短介绍一下自己。",
            "max_length": 1024,
            "temperature": 0.7,
            "top_p": 0.9,
            "history": [],
            "stream": False,
            "model": "qwen-turbo"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"API响应成功！返回内容：\n{result['text']}")
    else:
        print(f"API请求失败，状态码：{response.status_code}")
        print(response.text)

# 测试流式API
def test_stream_api():
    print("\n正在测试流式API...")
    response = requests.post(
        "http://localhost:8000/api/chat/stream",
        json={
            "prompt": "给我讲一个简短的小故事",
            "max_length": 1024,
            "temperature": 0.7,
            "top_p": 0.9,
            "history": [],
            "stream": True,
            "model": "qwen-turbo"
        },
        stream=True
    )
    
    if response.status_code == 200:
        print("开始接收流式响应：")
        full_text = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    try:
                        data = json.loads(line[5:])
                        if 'text' in data:
                            chunk = data['text']
                            full_text += chunk
                            # 实时打印内容
                            print(chunk, end='', flush=True)
                    except json.JSONDecodeError:
                        continue
        
        print("\n\n完整响应内容：")
        print(full_text)
    else:
        print(f"API请求失败，状态码：{response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # 检查API服务是否运行
    try:
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"API服务状态: {health_data['status']}")
            print(f"默认模型: {health_data['default_model']}")
            print(f"API配置状态: {'已配置' if health_data['api_configured'] else '未配置'}")
            print(f"使用OpenAI客户端: {'是' if health_data['using_openai_client'] else '否'}")
        else:
            print("API服务可能未启动或有问题")
            sys.exit(1)
    except requests.ConnectionError:
        print("无法连接到API服务，请确保服务已启动")
        sys.exit(1)
    
    # 先测试非流式API
    test_normal_api()
    
    # 再测试流式API
    test_stream_api() 