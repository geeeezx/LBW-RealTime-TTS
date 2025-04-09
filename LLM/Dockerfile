FROM python:3.11-slim

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 使用pip安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY main.py qwen_service.py .env.example ./

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 暴露服务端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 