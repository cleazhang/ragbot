# 使用硅基流动API配置指南

## 快速开始

### 1. 设置环境变量

```bash
export USE_SILICONFLOW=true
export SILICONFLOW_API_KEY=your_api_key_here
```

### 2. 启动应用

```bash
cd flask_app
python3 run.py
```

或者使用启动脚本：

```bash
./start.sh
```

## 配置说明

### 必需的环境变量

- `USE_SILICONFLOW`: 设置为 `true` 启用硅基流动API
- `SILICONFLOW_API_KEY`: 你的硅基流动API密钥

### 可选的环境变量

- `SILICONFLOW_MODEL`: 模型名称（默认：`Qwen/QwQ-32B`）
  - 其他可用模型：`Qwen/Qwen2.5-72B-Instruct`、`deepseek-ai/DeepSeek-V3` 等
- `SILICONFLOW_API_URL`: API地址（默认：`https://api.siliconflow.cn/v1/chat/completions`）

## 完整示例

```bash
# 设置环境变量
export USE_SILICONFLOW=true
export SILICONFLOW_API_KEY=sk-ziyyhopxmxuffgjgwphatkqjxftfenxvmlhpcycnzisdxyrr
export SILICONFLOW_MODEL=Qwen/QwQ-32B

# 启动应用
cd flask_app
python3 run.py
```

## 模型选择

硅基流动支持多种模型，你可以根据需求选择：

- `Qwen/QwQ-32B` - 默认模型，性能优秀
- `Qwen/Qwen2.5-72B-Instruct` - 更强的推理能力
- `deepseek-ai/DeepSeek-V3` - DeepSeek系列
- 更多模型请查看 [硅基流动官网](https://siliconflow.cn)

## 优势

✅ **响应速度快** - API调用，无需本地部署模型  
✅ **中文支持好** - 针对中文场景优化  
✅ **使用简单** - 只需设置API密钥即可  
✅ **成本可控** - 按使用量付费  

## 故障排查

### API调用失败

1. **检查API密钥**
   ```bash
   echo $SILICONFLOW_API_KEY
   ```
   确保密钥正确且未过期

2. **检查网络连接**
   ```bash
   curl https://api.siliconflow.cn/v1/models
   ```
   确保能访问硅基流动API

3. **查看日志**
   启动应用后，控制台会显示详细的错误信息

### 模型不可用

如果指定的模型不可用，系统会自动回退到本地模型。检查控制台日志查看具体错误。

## 与本地模型对比

| 特性 | 硅基流动API | 本地模型 |
|------|-----------|---------|
| 响应速度 | ⚡ 快（网络延迟） | 🐌 慢（本地推理） |
| 中文支持 | ✅ 优秀 | ✅ 良好 |
| 硬件要求 | 无 | 需要GPU |
| 成本 | 按使用量 | 一次性硬件成本 |
| 隐私 | 数据发送到API | 完全本地 |

## 更多信息

- [硅基流动官网](https://siliconflow.cn)
- [API文档](https://siliconflow.cn/docs)
- [模型列表](https://siliconflow.cn/models)

