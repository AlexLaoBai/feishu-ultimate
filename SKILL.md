---
name: feishu-ultimate
description: |
  飞书终极统一技能 - 整合并优化了4个飞书技能的所有功能
  
  整合来源 / Integrated From:
  - feishu-card (v1.4.11) - 交互式卡片
  - feishu-smart-doc-writer (v1.4.1) - 智能文档写入
  - feishu-message (v1.0.5) - 消息工具包
  - feishu-proactive-messenger (v1.0.1) - 主动消息发送
  
  核心优化 / Core Optimizations:
  - 统一Token管理（缓存、自动刷新）
  - 统一API调用（带重试、错误处理）
  - 统一安全扫描（防泄漏）
  - 统一错误处理
  - Python统一实现（避免Node.js和Python混用）
  
  功能模块 / Features:
  - 消息发送（文本/卡片/音频）
  - 消息获取（支持递归）
  - 文档管理（智能分块、所有权转移）
  - 群聊管理（创建、解散、信息）
  - 索引管理（自动索引、搜索）
---

# Feishu Ultimate | 飞书终极统一技能 v2.0.0

## 🚀 概述 Overview

本技能整合并优化了4个飞书技能的所有功能，去除了冗余代码，统一了架构，提供更高效、更易维护的飞书API操作。

This skill integrates and optimizes all features from 4 Feishu skills, removes redundant code, unifies architecture, and provides more efficient and maintainable Feishu API operations.

## ✨ 核心特性 Core Features

### 1. 统一架构 Unified Architecture
- ✅ Python统一实现（避免Node.js和Python混用）
- ✅ 统一Token管理（缓存、自动刷新）
- ✅ 统一API客户端（带重试、错误处理）
- ✅ 统一安全扫描（防泄漏）
- ✅ 模块化设计（message/document/group/index）

### 2. 消息模块 Message Module
- 发送文本消息
- 发送交互式卡片（Markdown、按钮、图片）
- 发送音频消息
- 获取消息（支持递归获取合并消息）
- 主动发送（支持多时境）

### 3. 文档模块 Document Module
- 智能文档创建（自动分块）
- 追加内容（自动分块）
- 自动所有权转移
- 自动索引更新
- 自动分类标签
- 表格转文本

### 4. 群聊模块 Group Module
- 创建群聊
- 解散群聊
- 获取群信息
- 列出置顶消息

### 5. 索引模块 Index Module
- 自动文档索引
- 搜索文档
- 列出文档

## 📋 工具列表 Tools

### 消息发送 Tools

#### send_text - 发送文本消息
Send text message to user or group.
发送文本消息到用户或群组。

```json
{
  "receive_id": "ou_xxx or oc_xxx",
  "text": "Message content / 消息内容",
  "receive_id_type": "open_id or chat_id (auto-detected if omitted)"
}
```

#### send_card - 发送交互式卡片
Send rich interactive card with Markdown, buttons, images.
发送富文本交互式卡片（支持Markdown、按钮、图片）。

```json
{
  "receive_id": "ou_xxx or oc_xxx",
  "title": "Card title / 卡片标题",
  "content": "Markdown content / Markdown内容",
  "color": "blue|red|orange|green|purple|grey",
  "button_text": "Button text / 按钮文本",
  "button_url": "Button URL / 按钮链接",
  "image_path": "/path/to/image.png"
}
```

#### send_audio - 发送音频消息
Send audio file as voice bubble.
发送音频文件作为语音消息。

```json
{
  "receive_id": "ou_xxx or oc_xxx",
  "file_path": "/path/to/audio.mp3",
  "duration_ms": 12345
}
```

### 消息获取 Tools

#### get_message - 获取消息
Fetch message content by ID.
根据ID获取消息内容。

```json
{
  "message_id": "om_xxx",
  "recursive": false,
  "raw": false
}
```

#### list_pins - 列出置顶消息
List pinned messages in a chat.
列出群聊中的置顶消息。

```json
{
  "chat_id": "oc_xxx"
}
```

### 文档管理 Tools

#### create_doc - 创建文档
Create document with auto-chunk writing.
创建文档（自动分块写入）。

```json
{
  "title": "Document title / 文档标题",
  "content": "Document content / 文档内容",
  "folder_token": "folder_token (optional)",
  "owner_openid": "ou_xxx (optional, auto-transfer ownership if provided)",
  "update_index": true
}
```

#### append_doc - 追加文档内容
Append content to existing document with auto-chunk.
追加内容到现有文档（自动分块）。

```json
{
  "doc_url": "https://feishu.cn/docx/xxx",
  "content": "Content to append / 要追加的内容"
}
```

#### transfer_ownership - 转移所有权
Transfer document ownership to user.
转移文档所有权给用户。

```json
{
  "doc_url": "https://feishu.cn/docx/xxx",
  "owner_openid": "ou_xxx"
}
```

### 索引管理 Tools

#### search_docs - 搜索文档
Search documents in local index.
搜索本地索引中的文档。

```json
{
  "keyword": "Search keyword / 搜索关键词"
}
```

#### list_docs - 列出文档
List all documents with optional filters.
列出所有文档（支持筛选）。

```json
{
  "tag": "AI Tech / AI技术 (optional)",
  "status": "Completed / 已完成 (optional)"
}
```

### 群聊管理 Tools

#### create_group - 创建群聊
Create new group chat.
创建新群聊。

```json
{
  "name": "Group name / 群名称",
  "user_ids": ["ou_xxx", "ou_xxx"],
  "description": "Group description / 群描述"
}
```

#### get_group_info - 获取群信息
Get group chat information.
获取群聊信息。

```json
{
  "chat_id": "oc_xxx"
}
```

## 🚀 快速开始 Quick Start

### 发送消息 Send Message

```bash
/feishu-ultimate send_text
receive_id: ou_xxx
text: Hello World!
```

### 发送卡片 Send Card

```bash
/feishu-ultimate send_card
receive_id: ou_xxx
title: Test Card
content: # Heading\n\nContent with **bold** and `code`.
color: blue
```

### 创建文档 Create Document

```bash
/feishu-ultimate create_doc
title: My Document
content: # Introduction\n\nThis is a long document...
owner_openid: ou_xxx
update_index: true
```

### 搜索文档 Search Documents

```bash
/feishu-ultimate search_docs
keyword: AI Tech
```

## 🔧 配置 Configuration

### 环境变量 Environment Variables

```bash
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_DEFAULT_TARGET=ou_xxx
```

### OpenClaw配置文件 OpenClaw Config

```json
{
  "channels": {
    "feishu": {
      "accounts": {
        "default": {
          "appId": "cli_xxx",
          "appSecret": "xxx",
          "defaultTo": "user:ou_xxx"
        }
      }
    }
  }
}
```

## 📦 架构 Architecture

```
feishu-ultimate/
├── SKILL.md              # 文档
├── __init__.py           # 初始化
├── feishu_common.py      # 公共模块
│   ├── TokenManager      # Token管理
│   ├── APIClient         # API客户端
│   └── SecurityScanner   # 安全扫描
├── message/              # 消息模块
│   ├── sender.py         # 消息发送
│   └── getter.py         # 消息获取
├── document/             # 文档模块
│   ├── writer.py         # 文档写入器
│   ├── chunker.py        # 分块器
│   └── transfer.py       # 所有权转移
├── group/                # 群聊模块
│   └── manager.py        # 群聊管理
└── index/                # 索引模块
    └── manager.py        # 索引管理
```

## 🔒 安全 Security

- ✅ 自动安全扫描（检测secret泄漏）
- ✅ Token缓存（减少API调用）
- ✅ 错误重试（提高可靠性）
- ✅ 敏感信息脱敏（日志不暴露）

## 📝 版本历史 Version History

### v2.0.0 (2026-03-08)
- ✅ 整合4个飞书技能的所有功能
- ✅ 统一Python实现
- ✅ 统一Token管理和API客户端
- ✅ 统一安全扫描和错误处理
- ✅ 模块化架构设计

### 来源版本 Source Versions
- feishu-card v1.4.11
- feishu-smart-doc-writer v1.4.1
- feishu-message v1.0.5
- feishu-proactive-messenger v1.0.1

## 📞 支持 Support

如有问题，请检查：
1. FEISHU_APP_ID 和 FEISHU_APP_SECRET 是否配置
2. Token缓存文件是否可写
3. 网络连接是否正常
4. 权限是否已开通

For issues, please check:
1. FEISHU_APP_ID and FEISHU_APP_SECRET are configured
2. Token cache file is writable
3. Network connection is working
4. Permissions are enabled
