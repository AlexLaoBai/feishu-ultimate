---
name: feishu-ultimate
description: |
  飞书终极统一技能 v3.0.0 — 整合并优化了所有飞书相关技能
  
  整合来源 / Integrated From:
  - feishu-card (v1.4.11) - 交互式卡片 + Persona卡片
  - feishu-smart-doc-writer (v1.4.1) - 智能文档写入 + 索引管理
  - feishu-message / feishu-messaging (v1.0.5) - 消息工具包
  - feishu-proactive-messenger (v1.0.1) - 主动消息发送
  - feishu-im - 飞书IM全功能（25+能力）
  - feishu-calendar-v1.0 - 日历管理（OAuth用户级）
  - feishu-doc-manager - 文档权限管理
  - alextangson/feishu_skills/feishu-bitable - 多维表格
  
  核心优化 / Core Optimizations:
  - 统一 Token 管理（缓存、自动刷新）
  - 统一 API 调用（带重试、错误处理）
  - 统一安全扫描（防泄漏）
  - 统一错误处理
  - Python 统一实现（避免 Node.js 和 Python 混用）
  
  功能模块 / Features:
  - 消息发送（文本/卡片/音频/图片/文件）
  - 消息获取（支持递归）
  - 消息操作（置顶/撤回/加急/回应/批量发送/系统消息）
  - 主动消息发送（支持多 Agent / --agent 参数）
  - 文档管理（智能分块、所有权转移）
  - Block 操作（读取、修改、删除、新增）
  - 评论管理（列出、创建、删除、回复）
  - 群聊管理（创建/解散/拉人/公告/菜单/Tab/组件）
  - 文档权限管理（添加/移除协作者）
  - 多维表格 Bitable（记录/字段/表/视图/权限）
  - 日历管理（OAuth 用户级日程）
  - 索引管理（自动索引、搜索）
---

# Feishu Ultimate | 飞书终极统一技能 v3.0.0

> 唯一需要安装的飞书技能。所有其他飞书 skill 已整合至此。

## 🚀 概述 Overview

本技能整合了 7 个飞书技能的全部功能，去除所有冗余，提供一套统一、高效的飞书 API 操作能力。

This skill integrates all features from 7 Feishu skills into one unified skill.

## ⚠️ 使用规范（重要）

**所有外部操作完成后必须交叉验证：**
- 📄 文档写入 → 调用 `list_blocks` 确认 block_count > 1
- 💬 消息发送 → 确认 returned `messageId`
- 📊 表格记录 → 调用 `list_records` 确认记录存在
- 🔄 任何 write 操作 → 立即 read 验证结果再交付用户

**禁止直接交付未验证的结果。** 工具返回成功 ≠ 操作成功，必须读回确认。

## ✨ 功能矩阵 Feature Matrix

| 模块 | 功能数 | 说明 |
|------|--------|------|
| 消息发送 | 6 | 文本、卡片、音频、图片、文件、主动发送 |
| 消息操作 | 7 | 置顶、撤回、加急、回应、批量发送、系统消息、获取 |
| 群聊管理 | 10 | 创建/解散、拉人/移除、公告、菜单、Tab、组件、搜索、成员 |
| 文档管理 | 9 | 创建、追加、Block CRUD、权限、评论 |
| 多维表格 | 14 | 表/字段/记录/视图/权限 全套 |
| 日历管理 | 4 | 创建/查询/删除日程、OAuth 用户级 |
| 索引管理 | 2 | 自动索引、搜索 |

---

## 📋 工具全表 Tools

### 💬 消息发送

#### send_text — 发送文本消息
```
receive_id: open_id 或群ID
text: 消息内容
receive_id_type: open_id / chat_id（自动识别）
```

#### send_card — 发送交互式卡片
支持 Markdown、按钮、图片，自动渲染格式。
```
receive_id: open_id 或群ID
title: 卡片标题
content: Markdown 内容（**加粗**、`代码`、# 标题均支持）
color: blue|red|orange|green|purple|grey（默认 blue）
button_text: 按钮文本（可选）
button_url: 按钮链接（可选）
image_path: 本地图片路径（可选，自动上传）
```

**卡片颜色对应场景：**
- `blue` — 日常通知
- `red` — 告警、失败
- `orange` — 警告
- `green` — 成功、完成
- `purple` — 特殊、创意
- `grey` — 低优先级

#### send_card_persona — Persona 风格卡片
预设人格化卡片（从 feishu-card 整合）：
```
receive_id: open_id
persona: d-guide | green-tea | mad-dog | default
text: 消息内容
```
- **d-guide**：红色警告头，加粗/代码前缀
- **green-tea**：胭脂红头，柔和可爱风
- **mad-dog**：灰色头，原始运行时错误风
- **default**：标准蓝色头

#### send_audio — 发送音频消息
```
receive_id: open_id 或群ID
file_path: /path/to/audio.mp3
duration_ms: 毫秒时长
```

#### send_image — 发送图片
上传图片并发送（从 feishu-messaging 整合）：
```
receive_id: open_id 或群ID
file_path: /path/to/image.jpg
```

#### send_file — 发送文件
上传文件并发送（支持 mp4/pdf/docx 等）：
```
receive_id: open_id 或群ID
file_path: /path/to/file.mp4
file_type: mp4（自动识别也可）
duration_ms: 视频时长ms（仅视频）
```

---

### 📩 主动消息发送（跨 Agent）

#### send_proactive — 主动发送消息
飞书渠道只支持被动回复，此工具补齐主动投递能力，支持多 Agent：
```
text: 消息内容
receive_id: open_id（可选，默认从 defaultTo 读取）
agent: agent_id（可选，如 coder/main/life，自动匹配凭证）
```

**工作原理：**
1. 通过 `--agent` 或 cwd 匹配确定 Agent ID
2. 从 `~/.openclaw/openclaw.json` 读取对应 appId/appSecret
3. 从 `defaultTo` 读取默认目标用户
4. 获取 tenant_access_token
5. 通过 `bot/v3/info` 获取 Bot 显示名
6. 调用飞书发送消息 API
7. 输出：`✅ [Bot名称] 消息已发送`

---

### 🔧 消息操作

#### get_message — 获取消息内容
```
message_id: 消息ID
recursive: false（是否递归合并消息）
raw: false（是否返回原始格式）
```

#### pin_message — 置顶消息
```
message_id: 消息ID
```

#### add_reaction — 消息回应（Reaction）
```
message_id: 消息ID
emoji_type: OK | THUMBSUP | HEART 等（大写标准ID）
```

#### recall_message — 撤回消息
仅能撤回机器人自己发送的消息：
```
message_id: 消息ID
```

#### urgent_message — 加急消息
向用户推送加急通知（消耗加急额度，慎用）：
```
message_id: 消息ID
user_id_list: ["ou_xxx"]
```

#### batch_send_message — 批量发送群消息
```
chat_id_list: ["oc_xxx", "oc_yyy"]
content: 消息内容
```

#### send_sys_message — 发送系统消息
在群中发送系统消息（视觉干扰低）：
```
chat_id: 群ID
content: 系统消息内容
```

---

### 👥 群聊管理

#### create_group — 创建群聊
```
name: 群名称
user_ids: ["ou_xxx"]（可选，同时拉人）
description: 群描述（可选）
```
**注意**：建群后建议紧接着调用 `add_group_members` 确保用户可见。

#### dissolve_group — 解散群聊
```
chat_id: 群ID
```

#### add_group_members — 拉人入群
```
chat_id: 群ID
member_ids: ["ou_xxx"]
member_id_type: open_id（默认）
```

#### remove_group_members — 移出群成员
```
chat_id: 群ID
member_ids: ["ou_xxx"]
```

#### get_group_members — 获取群成员列表
```
chat_id: 群ID
```

#### update_group_announcement — 更新群公告
```
chat_id: 群ID
content: 公告内容（支持富文本）
```

#### get_group_announcement — 获取群公告
```
chat_id: 群ID
```

#### create_group_menu — 创建群菜单
在群聊右上角添加自定义菜单：
```
chat_id: 群ID
menu_json: JSON菜单配置
```

#### create_group_tab — 创建群选项卡
在群聊中添加独立 Tab（多维表格看板、Wiki SOP）：
```
chat_id: 群ID
tab_json: JSON选项卡配置
```

#### search_group — 搜索群聊
按关键词搜索机器人可见的群：
```
query: 搜索关键词
page_size: 20（默认）
```

---

### 📄 文档管理

> ⚠️ **`create_doc` 与 `append_doc` 必须配套使用**（已踩坑，2026-03-26）
>
> `create_doc` 的 `content` 参数**不保证写入内容**（飞书 API 限制），正确流程：
> 1. 用 `create_doc` 创建**空文档**（只含标题）
> 2. 立即用 `append_doc` 追加内容
>
> **错误用法**：一次性传入 title + content → 文档标题有内容空白
> **正确用法**：create → append 两步走（参考下方示例）

#### create_doc — 创建文档（仅空壳，后续必须 append）
```
title: 文档标题
folder_token: 文件夹token（可选）
owner_openid: open_id（可选，自动转移所有权）
update_index: true（自动更新索引）
```
> ⚠️ `content` 参数传入会被忽略！创建后必须调用 `append_doc`

#### append_doc — 追加文档内容（创建后立即调用）
追加到现有文档（自动分块）：
```
doc_url: https://feishu.cn/docx/xxx
content: 要追加的内容
```

**标准用法示例：**
```python
# Step 1: 创建空文档
result = feishu_doc(action="create", title="我的文章")
doc_token = result["document_id"]
doc_url  = result["url"]

# Step 2: 立即追加内容（必须！）
feishu_doc(action="append", doc_token=doc_token, content=完整内容)

# Step 3: 交叉验证：读回内容确认写入成功
blocks = feishu_doc(action="list_blocks", doc_token=doc_token)
assert len(blocks) > 1, "⚠️ 内容写入失败，内容为空！"
```

#### list_blocks — 读取文档所有块

#### list_blocks — 读取文档所有块
返回完整 block 树（含表格、图片）：
```
doc_token: 文档ID
```

#### get_block — 读取单个块
```
doc_token: 文档ID
block_id: 块ID
```

#### update_block — 更新块文本
```
doc_token: 文档ID
block_id: 块ID
content: 新的文本内容
```

#### delete_block — 删除块
```
doc_token: 文档ID
block_id: 块ID
```

#### blocks_to_text — Block 转文本
将 block 树转换为可读纯文本（含标题层级、列表、代码块）。

---

### 🔐 文档权限管理

#### add_collaborator — 添加协作者
```
doc_url: https://feishu.cn/docx/xxx
member_id: open_id
perm: view | edit | full_access
```

#### remove_collaborator — 移除协作者
```
doc_url: https://feishu.cn/docx/xxx
member_id: open_id
```

#### list_collaborators — 列出协作者
```
doc_url: https://feishu.cn/docx/xxx
```

#### transfer_ownership — 转移所有权
```
doc_url: https://feishu.cn/docx/xxx
owner_openid: open_id
```

---

### 💬 评论管理

#### list_comments — 列出评论
```
doc_token: 文档ID
```

#### create_comment — 创建评论
```
doc_token: 文档ID
content: 评论内容
reply_to: 评论ID（可选，回复某条评论）
```

#### get_comment — 获取评论
```
doc_token: 文档ID
comment_id: 评论ID
```

#### delete_comment — 删除评论
```
doc_token: 文档ID
comment_id: 评论ID
```

#### list_replies — 获取评论回复
```
doc_token: 文档ID
comment_id: 评论ID
```

---

### 📊 多维表格 Bitable

#### create_bitable — 创建多维表格
```
name: 名称
folder_token: 文件夹token（可选）
```

#### list_tables — 列出数据表
```
bitable_url: https://xxx.feishu.cn/base/app_token
```

#### create_table — 新增数据表
```
bitable_url: https://xxx.feishu.cn/base/app_token
table_name: 表名
```

#### list_records — 列出记录
```
bitable_url: https://xxx.feishu.cn/base/app_token?table=tblxxx
page_size: 100（默认）
```

#### search_records — 搜索记录
```
bitable_url: https://xxx.feishu.cn/base/app_token?table=tblxxx
filter_json: [{"field_name":"状态","operator":"is","value":"进行中"}]
sort_json: [{"field_name":"金额","desc":true}]
```

#### create_record — 新增记录
```
bitable_url: https://xxx.feishu.cn/base/app_token?table=tblxxx
fields: {"名称":"测试","金额":100,"状态":"进行中","完成":true,"负责人":[{"id":"ou_xxx"}],"日期":1770508800000}
```
⚠️ 日期必须是 13 位毫秒时间戳

#### batch_create_records — 批量新增
```
bitable_url: https://xxx.feishu.cn/base/app_token?table=tblxxx
records: [{"fields":{"名称":"A"}},{"fields":{"名称":"B"}}]
```

#### update_record — 更新记录
```
bitable_url: https://xxx.feishu.cn/base/app_token?table=tblxxx
record_id: recxxx
fields: {"状态":"已完成"}
```

#### delete_records — 批量删除
```
bitable_url: https://xxx.feishu.cn/base/app_token?table=tblxxx
record_ids: ["recxxx1","recxxx2"]
```

#### list_fields — 列出字段
```
bitable_url: https://xxx.feishu.cn/base/app_token?table=tblxxx
```

#### create_field — 新增字段
```
bitable_url: https://xxx.feishu.cn/base/app_token?table=tblxxx
field_name: 新字段
field_type: 1（1=文本,2=数字,3=单选,4=多选,5=日期,7=复选框,11=人员）
property: {}（可选，字段属性）
```

#### list_views — 列出视图
```
bitable_url: https://xxx.feishu.cn/base/app_token?table=tblxxx
```

#### create_view — 创建视图
```
bitable_url: https://xxx.feishu.cn/base/app_token?table=tblxxx
view_name: 视图名
view_type: grid | kanban | gallery | gantt
```

#### add_bitable_collaborator — 添加协作者
```
bitable_url: https://xxx.feishu.cn/base/app_token
member_id: ou_xxx
perm: view | edit | full_access
```

---

### 📅 日历管理（OAuth 用户级）

飞书日历支持 OAuth 用户授权，可直接在用户个人日历中创建日程。

#### create_calendar_event — 创建日程
```
summary: 日程标题
start_time: 2026-03-25T15:00:00
end_time: 2026-03-25T16:00:00
description: 日程描述（可选）
location: 地点（可选）
reminder_minutes: 15（提前提醒分钟，可选）
```
支持自然语言时间解析：「明天下午3点」「下周五晚上6点」。

#### list_calendar_events — 查询日程
```
start_time: 开始时间（ISO格式）
end_time: 结束时间（ISO格式）
```

#### delete_calendar_event — 删除日程
```
event_id: 日程ID
```

#### OAuth 授权 — 首次使用
日历功能需要 OAuth 用户授权：
1. 配置 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`
2. 运行授权流程获取 user access token
3. token 保存在 `user-tokens.json`
4. Access Token 有效期 2 小时，Refresh Token 有效期 7 天

---

### 🔍 索引管理

#### search_docs — 搜索本地索引
```
keyword: 关键词
```

#### list_docs — 列出文档
```
tag: 标签（可选）
status: 状态（可选）
```

自动分类标签：AI技术、OpenClaw、飞书文档、电商、健康运动、每日归档

---

## 🔧 配置 Configuration

### 环境变量
```bash
FEISHU_APP_ID="your-app-id"
FEISHU_APP_SECRET="your-app-secret"
FEISHU_USER_TOKEN_FILE="user-tokens.json"  # 日历功能用
```

### OpenClaw 配置
```json
{
  "channels": {
    "feishu": {
      "accounts": {
        "default": {
          "appId": "your-app-id",
          "appSecret": "your-app-secret",
          "defaultTo": "user:ou_xxx"
        }
      }
    }
  }
}
```

### 主动消息（多 Agent）
支持通过 `--agent` 参数指定 Agent，自动从 `~/.openclaw/openclaw.json` 匹配对应凭证：
```bash
python3 feishu_proactive_messenger.py --agent coder --text "任务完成"
```

---

## 📦 架构 Architecture

```
feishu-ultimate/
├── SKILL.md              # 本文档
├── __init__.py
├── feishu_common.py      # 公共模块（Token、API Client、安全扫描）
├── message/
│   ├── sender.py         # 消息发送
│   ├── getter.py         # 消息获取
│   └── proactive.py      # 主动消息（多Agent）
├── document/
│   ├── writer.py         # 文档写入
│   ├── chunker.py        # 分块器
│   ├── block.py          # Block操作
│   ├── comment.py        # 评论管理
│   └── transfer.py       # 所有权 + 权限
├── group/
│   └── manager.py        # 群聊管理（全功能）
├── bitable/
│   ├── client.py         # Bitable客户端
│   ├── record.py         # 记录管理
│   ├── field.py          # 字段管理
│   ├── table.py          # 表管理
│   ├── view.py           # 视图管理
│   └── permission.py     # 权限管理
├── calendar/
│   └── manager.py        # 日历管理（OAuth）
├── index/
│   └── manager.py        # 索引管理
└── scripts/
    └── feishu_proactive_messenger.py  # 主动消息脚本
```

---

## 🔒 安全 Security

- ✅ 自动安全扫描（检测 secret 泄漏）
- ✅ Token 缓存（减少 API 调用）
- ✅ 错误重试（提高可靠性）
- ✅ 敏感信息脱敏（日志不暴露）
- ✅ 凭证不外传（仅用于获取 token 和发消息）

---

## 📝 版本历史

### v3.0.0 (2026-03-24)
- ✅ 整合 feishu-im 全部功能（置顶、撤回、加急、回应、批量发送、系统消息、群菜单/Tab/组件）
- ✅ 整合 feishu-messaging（搜索群聊、获取群成员、图片上传、文件上传）
- ✅ 整合 feishu-proactive-messenger（多 Agent 主动消息）
- ✅ 整合 feishu-calendar-v1.0（OAuth 用户级日历）
- ✅ 整合 feishu-card Persona 卡片（d-guide / green-tea / mad-dog）
- ✅ 整合 feishu-doc-manager 权限管理（add/remove/list_collaborator）
- ✅ 删除所有冗余飞书 skill，统一为 feishu-ultimate

### v2.1.0 (2026-03-23)
- ✅ 新增多维表格 Bitable 模块
- ✅ 新增 Block 操作
- ✅ 新增评论管理

### v2.0.0 (2026-03-08)
- ✅ 整合 4 个飞书技能

---

## ❓ 故障排除

| 问题 | 原因 | 解决 |
|------|------|------|
| 230001 无发送权限 | 机器人不在群中 | 先让用户和机器人对话 |
| 230002 消息不存在 | message_id 错误 | 检查 message_id |
| 99991663 token 过期 | token 过期 | 重新获取 tenant_access_token |
| open_id is not exist | 用错 user_id | 使用 `ou_` 开头的 open_id |
| 日历 401 | OAuth token 过期 | 用 refresh_token 刷新 |
