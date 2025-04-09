import os
import logging
import json
from typing import List, Dict, Optional, AsyncGenerator
import asyncio
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from qwen_service import QwenService

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="Qwen流式文本生成API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取API密钥和配置
QWEN_API_KEY = os.getenv("DASHSCOPE_API_KEY")
QWEN_API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
DEFAULT_MODEL = os.getenv("QWEN_MODEL", "qwen-turbo")
USE_OPENAI_CLIENT = os.getenv("USE_OPENAI_CLIENT", "true").lower() == "true"

# 初始化Qwen服务
qwen_service = QwenService(
    api_key=QWEN_API_KEY, 
    api_base=QWEN_API_BASE,
    use_openai_client=USE_OPENAI_CLIENT
)

# 请求模型
class ChatRequest(BaseModel):
    prompt: str
    max_length: int = Field(default=2048, description="生成文本的最大长度")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="温度参数，控制随机性")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="top-p采样参数")
    history: Optional[List[Dict[str, str]]] = Field(default=None, description="对话历史")
    stream: bool = Field(default=True, description="是否使用流式生成")
    model: str = Field(default=DEFAULT_MODEL, description="使用的模型，如qwen-turbo, qwen-plus, qwen-max等")

# 响应模型
class ChatResponse(BaseModel):
    text: str

@app.get("/")
def read_root():
    """根路径，返回API信息"""
    return {
        "message": "欢迎使用Qwen流式文本生成API", 
        "default_model": DEFAULT_MODEL,
        "api_configured": bool(QWEN_API_KEY),
        "using_openai_client": USE_OPENAI_CLIENT
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """非流式聊天接口"""
    if request.stream:
        raise HTTPException(status_code=400, detail="该接口不支持流式生成，请使用 /api/chat/stream")
    
    try:
        # 调用Qwen服务生成文本
        response = qwen_service.generate(
            prompt=request.prompt,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            history=request.history,
            model=request.model
        )
        return ChatResponse(text=response)
    except Exception as e:
        logger.error(f"生成文本时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成文本时出错: {str(e)}")

async def generate_stream_response(request: ChatRequest) -> AsyncGenerator[str, None]:
    """异步生成流式响应"""
    try:
        # 使用Qwen服务的流式生成
        for text_chunk in qwen_service.generate_stream(
            prompt=request.prompt,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p,
            history=request.history,
            model=request.model
        ):
            # 构造SSE事件数据
            yield json.dumps({"text": text_chunk})
            # 加入一个小的延迟，以模拟真实的流式生成
            await asyncio.sleep(0.01)
    except Exception as e:
        logger.error(f"流式生成文本时出错: {str(e)}")
        yield json.dumps({"error": str(e)})

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天接口"""
    if not request.stream:
        raise HTTPException(status_code=400, detail="该接口仅支持流式生成，请使用 /api/chat")
    
    # 返回流式响应
    return EventSourceResponse(
        generate_stream_response(request),
        media_type="text/event-stream"
    )

# 健康检查接口
@app.get("/health")
def health_check():
    """健康检查接口"""
    return {
        "status": "healthy", 
        "default_model": DEFAULT_MODEL, 
        "api_configured": bool(QWEN_API_KEY),
        "using_openai_client": USE_OPENAI_CLIENT
    }

if __name__ == "__main__":
    import uvicorn
    # 启动服务器
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 