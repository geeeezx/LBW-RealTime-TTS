from typing import List, Iterator, Dict, Any, Optional
import os
import logging
import json
import time
from dotenv import load_dotenv
import requests

# 尝试导入OpenAI库，如果不可用则使用请求库
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class QwenService:
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, use_openai_client: bool = True):
        """
        初始化Qwen API服务
        
        Args:
            api_key: Qwen API密钥，如果为None则从环境变量DASHSCOPE_API_KEY获取
            api_base: Qwen API基础URL，如果为None则使用默认值
            use_openai_client: 是否使用OpenAI客户端库，如果为False则使用requests直接调用
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        # 基础URL，使用兼容OpenAI的接口
        self.api_base = api_base or os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.use_openai_client = use_openai_client and OPENAI_AVAILABLE
        self.client = None

        if not self.api_key:
            logger.warning("未提供API密钥，请设置DASHSCOPE_API_KEY环境变量或在初始化时提供")
        
        # 如果使用OpenAI客户端，初始化客户端
        if self.use_openai_client:
            if not OPENAI_AVAILABLE:
                logger.warning("未安装OpenAI客户端库，将使用requests直接调用API")
                self.use_openai_client = False
            else:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.api_base
                )
        
        logger.info(f"Qwen API服务已初始化，使用{'OpenAI客户端' if self.use_openai_client else 'requests'}调用")
    
    def generate_stream(
        self, 
        prompt: str,
        max_length: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9,
        history: Optional[List[Dict[str, str]]] = None,
        model: str = "qwen-turbo"
    ) -> Iterator[str]:
        """
        流式生成文本
        
        Args:
            prompt: 用户输入的提示
            max_length: 生成文本的最大长度
            temperature: 温度参数
            top_p: top-p采样参数
            history: 对话历史
            model: 使用的模型名称
            
        Returns:
            生成的文本流
        """
        if not self.api_key:
            raise ValueError("API密钥未设置，请设置DASHSCOPE_API_KEY环境变量或在初始化时提供")
        
        if history is None:
            history = []
            
        # 准备消息列表
        messages = []
        
        # 添加系统消息
        messages.append({"role": "system", "content": "You are a helpful assistant."})
        
        # 添加历史对话
        for entry in history:
            if "user" in entry:
                messages.append({"role": "user", "content": entry["user"]})
            if "assistant" in entry:
                messages.append({"role": "assistant", "content": entry["assistant"]})
        
        # 添加当前用户提问
        messages.append({"role": "user", "content": prompt})
        
        if self.use_openai_client:
            # 使用OpenAI客户端库调用
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_length,
                temperature=temperature,
                top_p=top_p,
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices and hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            # 使用requests直接调用API
            # 准备API请求参数 (兼容OpenAI格式)
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": max_length,
                "temperature": temperature,
                "top_p": top_p,
                "stream": True
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送API请求
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                stream=True
            )
            
            if response.status_code != 200:
                error_msg = f"API请求失败: HTTP {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data:'):
                        json_str = line[5:].strip()
                        if json_str and json_str != "[DONE]":
                            try:
                                result = json.loads(json_str)
                                if "choices" in result and len(result["choices"]) > 0:
                                    choice = result["choices"][0]
                                    if "delta" in choice and "content" in choice["delta"] and choice["delta"]["content"]:
                                        yield choice["delta"]["content"]
                            except json.JSONDecodeError:
                                logger.error(f"无法解析API响应: {json_str}")
    
    def generate(
        self, 
        prompt: str,
        max_length: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9,
        history: Optional[List[Dict[str, str]]] = None,
        model: str = "qwen-turbo"
    ) -> str:
        """
        生成文本（非流式）
        
        Args:
            prompt: 用户输入的提示
            max_length: 生成文本的最大长度
            temperature: 温度参数
            top_p: top-p采样参数
            history: 对话历史
            model: 使用的模型名称
            
        Returns:
            生成的完整文本
        """
        if not self.api_key:
            raise ValueError("API密钥未设置，请设置DASHSCOPE_API_KEY环境变量或在初始化时提供")
        
        if history is None:
            history = []
            
        # 准备消息列表
        messages = []
        
        # 添加系统消息
        messages.append({"role": "system", "content": "You are a helpful assistant."})
        
        # 添加历史对话
        for entry in history:
            if "user" in entry:
                messages.append({"role": "user", "content": entry["user"]})
            if "assistant" in entry:
                messages.append({"role": "assistant", "content": entry["assistant"]})
        
        # 添加当前用户提问
        messages.append({"role": "user", "content": prompt})
        
        if self.use_openai_client:
            # 使用OpenAI客户端库调用
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_length,
                temperature=temperature,
                top_p=top_p,
                stream=False
            )
            
            if completion.choices:
                return completion.choices[0].message.content
            else:
                raise Exception("API响应缺少content内容")
        else:
            # 使用requests直接调用API
            # 准备API请求参数 (兼容OpenAI格式)
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": max_length,
                "temperature": temperature,
                "top_p": top_p,
                "stream": False
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送API请求
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                error_msg = f"API请求失败: HTTP {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # 处理API响应
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"API响应格式不符合预期: {result}")
                raise Exception(f"API响应格式不符合预期: {result}") 