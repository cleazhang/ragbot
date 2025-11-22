## 任务目标
在上传的文档中，找到相关片段部分，将改部分传给大模型继续总结回复给用户
## 软硬件配置
显卡：rtx4090
操作系统：Ubuntu 22.04.4 LTS
langchain版本：0.1.16
文本大模型：chatglm4-9b-chat
## 环境配置
conda create --name rag --file requirements.txt
conda activate rag
## 启动本地的模型服务
conda create --name glm4 --file requirements_glm4.txt
conda activate glm4
在llm_models目录下：python glm4.py
## 使用rag检索
在flask_app目录下:python3 run.py
使用test进行测试

## 支持上传文件类型
目前支持txt和html和txt文件，word格式未测试，pdf不支持

##  urgency
- [ ] 文件和用户绑定功能
- [ ] 回复更换为流式输出
- [ ] 更新一下langchain版本

## TODO not urgency
- [ ] 检索效果不好，如何进行数据增强？
- [ ] 自己写一个向量库的class，更换查询索引
- [ ] 实现更多llm的接入
- [ ] 查询质量，生成质量评估
- [ ] 图片提取

# rag_
