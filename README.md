# Feishu Ultimate | 飞书终极统一技能

[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/AlexLaoBai/feishu-ultimate)
[![Python](https://img.shields.io/badge/python-3.8+-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

飞书终极统一技能 - 整合并优化了4个飞书技能的所有功能，去除冗余代码，提供更高效、更易维护的飞书API操作。

## ✨ 特性

### 整合来源
- [feishu-card](https://github.com/AlexLaoBai/feishu-ultimate) (v1.4.11) - 交互式卡片
- [feishu-smart-doc-writer](https://github.com/AlexLaoBai/feishu-ultimate) (v1.4.1) - 智能文档写入
- [feishu-message](https://github.com/AlexLaoBai/feishu-ultimate) (v1.0.5) - 消息工具包
- [feishu-proactive-messenger](https://github.com/AlexLaoBai/feishu-ultimate) (v1.0.1) - 主动消息发送

### 核心优化
- ✅ 统一Python实现（避免Node.js和Python混用）
- ✅ 统一Token管理（缓存、自动刷新）
- ✅ 统一API客户端（带重试、错误处理）
- ✅ 统一安全扫描（防止敏感信息泄漏）
- ✅ 模块化架构设计

## 📦 功能模块

### 1. 消息模块 (message)
- **发送文本消息** - 发送纯文本到用户或群组
- **发送交互式卡片** - 支持Markdown、按钮、图片
- **发送音频消息** - 自动检测音频时长
- **获取消息** - 支持递归获取合并消息
- **列出置顶消息** - 查看群聊置顶内容

### 2. 文档模块 (document)
- **智能文档创建** - 自动分块，解决长文档API限制
- **追加文档内容** - 自动分块追加
- **自动所有权转移** - 创建后自动转移给用户
- **自动索引更新** - 本地文档索引管理
- **自动分类标签** - 根据内容自动打标签

### 3. 群聊模块 (group)
- **创建群聊** - 创建新群并添加成员
- **解散群聊** - 解散指定群聊
- **获取群信息** - 查看群详情
- **群成员管理** - 添加/移除成员

### 4. 索引模块 (index)
- **文档索引** - 自动维护本地文档索引
- **搜索文档** - 按关键词搜索
- **列出文档** - 按标签、状态筛选

## 🚀 快速开始

### 安装依赖

```bash
pip install aiohttp music-metadata
```

### 配置环境变量

```bash
# 方式1: 环境变量
export FEISHU_APP_ID="cli_xxx"
export FEISHU_APP_SECRET="xxx"

# 方式2: OpenClaw配置 (自动读取)
# ~/.openclaw/openclaw.json
```

### 使用示例

#### 发送文本消息

```python
from feishu_ultimate.message.sender import send_text_message

await send_text_message(
    receive_id="ou_xxx",
    text="Hello World!"
)
```

#### 发送卡片消息

```python
from feishu_ultimate.message.sender import send_card_message

await send_card_message(
    receive_id="ou_xxx",
    title="标题",
    content="# Markdown内容\n\n**加粗**和`代码`",
    color="blue",
    button_text="点击这里",
    button_url="https://example.com"
)
```

#### 创建文档

```python
from feishu_ultimate.document.writer import create_feishu_document

result = await create_feishu_document(
    title="我的文档",
    content="# 标题\n\n这是文档内容...",
    owner_openid="ou_xxx",  # 可选：自动转移所有权
    update_index=True       # 可选：更新索引
)

print(result["doc_url"])  # 文档链接
```

#### 搜索文档

```python
from feishu_ultimate.index.manager import search_documents

results = search_documents("AI技术")
for doc in results:
    print(doc["name"], doc["link"])
```

## 📁 项目结构

```
feishu-ultimate/
├── SKILL.md                    # 技能完整文档
├── README.md                   # 本文件
├── __init__.py                # 入口
├── _meta.json                  # 元数据
├── feishu_common.py           # 公共模块
│   ├── TokenManager          # Token管理
IClient             #│   ├── AP API客户端
│   └── SecurityScanner       # 安全扫描
├── message/                   # 消息模块
│   ├── sender.py             # 消息发送
│   └── getter.py             # 消息获取
├── document/                  # 文档模块
│   ├── chunker.py            # 智能分块器
│   ├── writer.py              # 文档写入器
│   └── transfer.py            # 所有权转移
├── group/                     # 群聊模块
│   └── manager.py            # 群聊管理
└── index/                     # 索引模块
    └── manager.py            # 索引管理
```

## 🔧 OpenClaw 集成

本技能专为OpenClaw设计，可通过以下方式使用：

```bash
# 在OpenClaw中安装
skillhub install feishu-ultimate
```

或直接在OpenClaw会话中调用：

```
/feishu-ultimate send_text
receive_id: ou_xxx
text: Hello!
```

## 🔒 安全特性

- **Token缓存** - 减少API调用次数
- **自动刷新** - Token过期自动刷新
- **安全扫描** - 自动检测敏感信息泄漏
- **错误重试** - 网络错误自动重试
- **日志脱敏** - 日志不暴露敏感信息

## 📝 版本历史

### v2.0.0 (2026-03-08)
- ✅ 整合4个飞书技能的所有功能
- ✅ 统一Python实现
- ✅ 统一Token管理和API客户端
- ✅ 统一安全扫描和错误处理
- ✅ 模块化架构设计

## 📄 许可证

MIT License

## 👤 作者

AlexLaoBai (OpenClaw)

## 🤝 贡献

欢迎提交Issue和Pull Request！
