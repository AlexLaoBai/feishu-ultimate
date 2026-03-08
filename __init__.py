#!/usr/bin/env python3
"""
Feishu Ultimate - 飞书终极统一技能

整合并优化了4个飞书技能的所有功能：
- feishu-card (v1.4.11)
- feishu-smart-doc-writer (v1.4.1)
- feishu-message (v1.0.5)
- feishu-proactive-messenger (v1.0.1)

Version: 2.0.0
Author: OpenClaw AI
Date: 2026-03-08
"""

__version__ = "2.0.0"

# 导入公共模块
from .feishu_common import (
    TokenManager,
    APIClient,
    SecurityScanner,
    infer_receive_id_type,
    extract_doc_token_from_url,
)

# 导入子模块
from . import message
from . import document
from . import group
from . import index

__all__ = [
    "__version__",
    # 公共模块
    "TokenManager",
    "APIClient",
    "SecurityScanner",
    "infer_receive_id_type",
    "extract_doc_token_from_url",
    # 子模块
    "message",
    "document",
    "group",
    "index",
]
