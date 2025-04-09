import requests
import json

# 非流式测试
def test_regular_chat():
    url = "http://localhost:8000/api/chat"
    
    payload = {
        "prompt": "你好，请简单介绍一下自己",
        "stream": False,
        "model": "qwen-turbo"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

# 执行测试
if __name__ == "__main__":
    print("测试非流式API...")
    test_regular_chat() 