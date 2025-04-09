# Docker部署指南

本文档提供使用Docker部署Qwen流式文本生成微服务的详细步骤。

## 前提条件

- 安装Docker和Docker Compose
- 获取阿里云通义千问API密钥

## 部署步骤

### 1. 准备环境变量

创建`.env`文件（或复制`.env.example`并重命名为`.env`），填入您的API密钥：

```bash
# 复制示例环境变量文件
cp .env.example .env

# 编辑.env文件，填入您的API密钥
# DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. 构建并启动服务

```bash
# 构建Docker镜像
docker-compose build

# 启动服务
docker-compose up -d
```

服务将在后台运行，并在8000端口上提供API。

### 3. 验证服务状态

```bash
# 检查容器状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

### 4. 测试API

服务启动后，您可以使用curl或其他HTTP客户端测试API：

```bash
# 健康检查
curl http://localhost:8000/health

# 非流式文本生成
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"你好，请介绍一下自己","stream":false}'
```

对于流式API测试，建议使用项目中的`test_stream_api.py`脚本。

### 5. 停止服务

```bash
# 停止服务但不删除容器
docker-compose stop

# 停止服务并删除容器
docker-compose down
```

## 注意事项

1. 默认情况下，服务会使用OpenAI客户端库调用通义千问API。如果您不需要使用OpenAI客户端，可以在`.env`文件中设置`USE_OPENAI_CLIENT=false`。

2. 如果您需要更改默认端口，可以修改`docker-compose.yml`文件中的端口映射：
   ```yaml
   ports:
     - "新端口:8000"
   ```

3. 在生产环境中，建议配置反向代理（如Nginx）并添加HTTPS支持和适当的认证机制。

4. 如需更新服务，请执行以下步骤：
   ```bash
   # 拉取最新代码
   git pull

   # 重新构建并启动
   docker-compose down
   docker-compose build
   docker-compose up -d
   ``` 