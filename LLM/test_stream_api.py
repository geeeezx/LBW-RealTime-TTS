import requests
import json
import time

def test_stream_chat():
    url = "http://localhost:8000/api/chat/stream"
    
    payload = {
        "prompt": "用中文解释什么是机器学习",
        "stream": True,
        "model": "qwen-turbo"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    # 流式请求
    response = requests.post(url, json=payload, headers=headers, stream=True)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("流式响应内容:")
        full_text = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    try:
                        data = json.loads(line[5:])
                        text_chunk = data.get('text', '')
                        print(text_chunk, end='', flush=True)
                        full_text += text_chunk
                    except json.JSONDecodeError:
                        print(f"无法解析JSON: {line[5:]}")
        
        print("\n\n完整响应:")
        print(full_text)

if __name__ == "__main__":
    print("测试流式API...")
    test_stream_chat() 