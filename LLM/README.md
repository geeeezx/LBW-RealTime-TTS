# Qwen流式文本生成微服务

基于FastAPI和通义千问API的流式文本生成微服务。

## 功能特点

- 支持通义千问大模型的API调用
- 提供流式生成API，实时返回生成结果
- 支持对话历史记录
- 可调整温度、top-p等生成参数
- 跨域支持，可用于前端调用
- 提供健康检查接口
- 支持Docker部署

## 部署方式

### 方式一：Docker部署（推荐）

详细的Docker部署指南请查看 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)。

快速部署步骤：

```bash
# 1. 准备环境变量
cp .env.example .env
# 编辑.env文件，填入API密钥

# 2. 构建并启动服务
docker-compose build
docker-compose up -d
```

### 方式二：本地部署

#### 安装依赖

##### 快速设置（推荐）

我们提供了便捷的设置脚本，自动安装uv、创建虚拟环境并安装依赖：

Windows:
```bash
setup.bat
```

Linux/MacOS:
```bash
chmod +x setup.sh
./setup.sh
```

##### 手动设置

###### 使用uv包管理器

uv是一个用Rust编写的快速Python包管理器和虚拟环境工具。

```bash
# 安装uv (如果尚未安装)
curl -sSf https://install.ultraviolet.rs | sh

# 创建虚拟环境
uv venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (Linux/MacOS)
# source .venv/bin/activate

# 使用uv安装依赖
uv pip install -r requirements.txt
```

## 环境变量配置

创建`.env`文件或直接设置环境变量：

```
# 必填：阿里云通义千问API密钥
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx

# 可选：API基础URL (默认使用通义千问OpenAI兼容API)
# QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# 可选：默认使用的模型
# QWEN_MODEL=qwen-turbo
```

您需要在[阿里云通义千问](https://dashscope.console.aliyun.com/)申请API密钥。

## 启动服务

```bash
cd LLM
python main.py
```

或者使用uvicorn直接启动：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，可以通过 http://localhost:8000/docs 访问API文档。

## API接口

### 1. 非流式文本生成

- 接口：`POST /api/chat`
- 参数示例：

```json
{
  "prompt": "你好，请介绍一下自己",
  "max_length": 2048,
  "temperature": 0.7,
  "top_p": 0.9,
  "history": [],
  "stream": false,
  "model": "qwen-turbo"
}
```

### 2. 流式文本生成

- 接口：`POST /api/chat/stream`
- 参数示例：

```json
{
  "prompt": "你好，请介绍一下自己",
  "max_length": 2048,
  "temperature": 0.7,
  "top_p": 0.9,
  "history": [],
  "stream": true,
  "model": "qwen-turbo"
}
```

## 前端集成示例

使用JavaScript调用流式生成API：

```javascript
// 创建SSE连接
function createCompletionStream(prompt, options = {}) {
  const controller = new AbortController();
  const { signal } = controller;

  fetch('/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt,
      stream: true,
      ...options
    }),
    signal,
  }).then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    function readChunk() {
      reader.read().then(({ done, value }) => {
        if (done) {
          return;
        }
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        lines.forEach(line => {
          if (line.startsWith('data:')) {
            const data = JSON.parse(line.slice(5));
            // 处理接收到的文本片段
            console.log(data.text);
          }
        });
        
        readChunk();
      }).catch(error => {
        console.error('读取流时发生错误:', error);
      });
    }
    
    readChunk();
  }).catch(error => {
    console.error('请求流时发生错误:', error);
  });
  
  // 返回控制器，用于中断请求
  return controller;
}

// 使用示例
const controller = createCompletionStream('你好，请介绍一下自己');

// 中断生成
// controller.abort();
```

## 注意事项

1. 本服务调用阿里云通义千问API，需要有效的API密钥
2. 不同类型的模型（如qwen-turbo, qwen-plus, qwen-max）有不同的定价，详情请参考[阿里云官方文档](https://help.aliyun.com/zh/model-studio/pricing)
3. 使用uv可以显著加快依赖安装速度
4. 在生产环境中，建议使用HTTPS并添加适当的认证机制 