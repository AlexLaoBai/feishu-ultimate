#!/usr/bin/env python3
"""
Feishu Message Getter - 消息获取模块
获取消息、置顶消息等
"""

import json
import logging
from typing import Optional, Dict, Any, List

from ..feishu_common import TokenManager, APIClient


logger = logging.getLogger(__name__)


class MessageGetter:
    """消息获取器"""
    
    def __init__(self, token_manager: TokenManager):
        """
        初始化消息获取器
        
        Args:
            token_manager: Token管理器
        """
        self.token_manager = token_manager
        self.api_client = APIClient(token_manager)
    
    async def get_message(
        self,
        message_id: str,
        raw: bool = False,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        获取消息
        
        Args:
            message_id: 消息ID
            raw: 是否返回原始JSON
            recursive: 是否递归获取合并消息
            
        Returns:
            消息数据
        """
        logger.info(f"获取消息: {message_id}")
        
        # 调用API
        data = await self.api_client.get(f"/im/v1/messages/{message_id}")
        
        if raw:
            return data
        
        # 格式化输出
        if data.get("items") and len(data["items"]) > 0:
            # 合并消息容器
            items = data["items"]
            logger.info(f"📦 合并消息容器 ({len(items)} 条消息)")
            
            result = []
            for item in items:
                # 跳过容器自身
                if item.get("message_id") == message_id and len(items) > 1:
                    continue
                
                formatted = self._format_message(item, recursive=recursive)
                result.append(formatted)
            
            return {
                "type": "merged_forward",
                "count": len(result),
                "messages": result
            }
        else:
            # 单条消息
            formatted = self._format_message(
                data.get("items", [data])[0] if data.get("items") else data,
                recursive=recursive
            )
            return formatted
    
    def _format_message(
        self,
        msg: Dict[str, Any],
        depth: int = 0,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        格式化消息
        
        Args:
            msg: 原始消息数据
            depth: 递归深度
            recursive: 是否递归格式化
            
        Returns:
            格式化后的消息
        """
        indent = "  " * depth
        
        # 发送者信息
        sender_info = msg.get("sender", {})
        sender_type = sender_info.get("sender_type", "unknown")
        sender_id = sender_info.get("id", "unknown")
        
        if sender_type == "user":
            sender = f"User({sender_id})"
        elif sender_type == "app":
            sender = f"App({sender_id})"
        else:
            sender = sender_id
        
        # 时间戳
        create_time = msg.get("create_time", 0)
        time_str = self._format_timestamp(create_time)
        
        # 消息类型
        msg_type = msg.get("msg_type", "text")
        
        # 消息内容
        content = self._parse_content(msg.get("body", {}), msg_type)
        
        result = {
            "sender": sender,
            "time": time_str,
            "type": msg_type,
            "content": content
        }
        
        # 递归处理合并消息
        if msg_type == "merge_forward" and recursive:
            items = msg.get("items", [])
            nested_messages = []
            
            for item in items:
                nested = self._format_message(item, depth + 1, recursive)
                nested_messages.append(nested)
            
            result["messages"] = nested_messages
        
        return result
    
    def _parse_content(self, body: Dict[str, Any], msg_type: str) -> str:
        """
        解析消息内容
        
        Args:
            body: 消息body
            msg_type: 消息类型
            
        Returns:
            解析后的文本内容
        """
        try:
            content_str = body.get("content", "")
            if not content_str:
                return ""
            
            content_data = json.loads(content_str)
            
            # 文本消息
            if msg_type == "text":
                return content_data.get("text", "")
            
            # 帖子消息
            elif msg_type == "post":
                title = content_data.get("title", "")
                post_content = content_data.get("content", [])
                
                if post_content and isinstance(post_content, list):
                    text_parts = []
                    for paragraph in post_content:
                        if isinstance(paragraph, list):
                            text_parts.append(
                                "".join([
                                    element.get("text", "")
                                    for element in paragraph
                                    if isinstance(element, dict)
                                ])
                            )
                    
                    content_text = "\n".join(text_parts)
                    if title:
                        return f"[Post] {title}\n{content_text}"
                    return content_text
                
                return title
            
            # 图片消息
            elif msg_type == "image":
                image_key = content_data.get("image_key", "")
                return f"[Image key={image_key}]"
            
            # 音频消息
            elif msg_type == "audio":
                file_key = content_data.get("file_key", "")
                return f"[Audio file={file_key}]"
            
            # 视频消息
            elif msg_type == "video":
                file_key = content_data.get("file_key", "")
                return f"[Video file={file_key}]"
            
            # 文件消息
            elif msg_type == "file":
                file_key = content_data.get("file_key", "")
                file_name = content_data.get("file_name", "")
                return f"[File {file_name} key={file_key}]"
            
            # 交互式卡片
            elif msg_type == "interactive":
                # 尝试提取markdown内容
                elements = content_data.get("elements", [])
                text_parts = []
                
                for element in elements:
                    if element.get("tag") == "markdown":
                        text_parts.append(element.get("content", ""))
                
                if text_parts:
                    return "\n".join(text_parts)
                
                return "[Interactive Card]"
            
            # 合并消息
            elif msg_type == "merge_forward":
                return "[Merged Forward]"
            
            # 默认返回原始内容
            return content_str
            
        except json.JSONDecodeError:
            return str(content_str)
        except Exception as e:
            logger.warning(f"解析内容失败: {e}")
            return str(body.get("content", ""))
    
    def _format_timestamp(self, timestamp: int) -> str:
        """
        格式化时间戳
        
        Args:
            timestamp: 毫秒级时间戳
            
        Returns:
            格式化后的时间字符串
        """
        try:
            import datetime
            dt = datetime.datetime.fromtimestamp(timestamp / 1000)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(timestamp)
    
    async def list_pins(self, chat_id: str) -> List[Dict[str, Any]]:
        """
        列出群聊的置顶消息
        
        Args:
            chat_id: 群聊ID
            
        Returns:
            置顶消息列表
        """
        logger.info(f"列出置顶消息: {chat_id}")
        
        # 调用API
        data = await self.api_client.get(
            f"/im/v1/pins",
            params={"chat_id": chat_id}
        )
        
        # 解析置顶消息
        items = data.get("items", [])
        result = []
        
        for item in items:
            pinned_msg = self._format_message(item.get("message", {}))
            pinned_msg["pin_type"] = item.get("pin_type", "")
            pinned_msg["pinned_by"] = item.get("pinned_by", {})
            
            result.append(pinned_msg)
        
        logger.info(f"找到 {len(result)} 条置顶消息")
        return result
    
    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """
        获取群聊信息
        
        Args:
            chat_id: 群聊ID
            
        Returns:
            群聊信息
        """
        logger.info(f"获取群聊信息: {chat_id}")
        
        # 调用API
        return await self.api_client.get(f"/im/v1/chats/{chat_id}")
    
    async def get_chat_members(
        self,
        chat_id: str,
        page_size: int = 50,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取群聊成员
        
        Args:
            chat_id: 群聊ID
            page_size: 每页数量
            page_token: 分页token
            
        Returns:
            成员列表
        """
        logger.info(f"获取群聊成员: {chat_id}")
        
        params = {
            "page_size": page_size
        }
        if page_token:
            params["page_token"] = page_token
        
        return await self.api_client.get(
            f"/im/v1/chats/{chat_id}/members",
            params=params
        )


# 便捷函数
async def get_message_detail(message_id: str, **kwargs) -> Dict[str, Any]:
    """获取消息（便捷函数）"""
    token_manager = TokenManager.load_from_config()
    getter = MessageGetter(token_manager)
    return await getter.get_message(message_id, **kwargs)


async def list_pinned_messages(chat_id: str) -> List[Dict[str, Any]]:
    """列出置顶消息（便捷函数）"""
    token_manager = TokenManager.load_from_config()
    getter = MessageGetter(token_manager)
    return await getter.list_pins(chat_id)
