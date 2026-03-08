#!/usr/bin/env python3
"""
Feishu Group Manager - 群聊管理模块
创建、解散、获取群聊信息
"""

import logging
from typing import Optional, List, Dict, Any

from ..feishu_common import (
    TokenManager,
    APIClient,
    infer_receive_id_type,
)


logger = logging.getLogger(__name__)


class GroupManager:
    """群聊管理器"""
    
    def __init__(self, token_manager: TokenManager):
        """
        初始化群聊管理器
        
        Args:
            token_manager: Token管理器
        """
        self.token_manager = token_manager
        self.api_client = APIClient(token_manager)
    
    async def create_group(
        self,
        name: str,
        user_ids: List[str],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建群聊
        
        Args:
            name: 群名称
            user_ids: 用户ID列表
            description: 群描述（可选）
            
        Returns:
            群聊信息
        """
        logger.info(f"创建群聊: {name}")
        
        # 构建请求
        data = {
            "name": name,
            "user_id_type": "open_id",
            "member_id_type": "open_id"
        }
        
        # 添加成员
        if user_ids:
            data["member_ids"] = user_ids
        
        # 添加描述
        if description:
            data["description"] = description
        
        # 调用API
        result = await self.api_client.post("/im/v1/chats", data=data)
        
        chat_id = result.get("chat_id")
        logger.info(f"✅ 群聊创建成功: {chat_id}")
        
        return {
            "chat_id": chat_id,
            "name": name,
            "description": description,
            "member_count": len(user_ids) if user_ids else 0
        }
    
    async def disband_group(self, chat_id: str) -> bool:
        """
        解散群聊
        
        Args:
            chat_id: 群聊ID
            
        Returns:
            是否成功
        """
        logger.info(f"解散群聊: {chat_id}")
        
        # 调用API
        await self.api_client.post(f"/im/v1/chats/{chat_id}")
        
        logger.info(f"✅ 群聊已解散: {chat_id}")
        return True
    
    async def get_group_info(self, chat_id: str) -> Dict[str, Any]:
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
    
    async def list_group_members(
        self,
        chat_id: str,
        page_size: int = 50,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        列出群聊成员
        
        Args:
            chat_id: 群聊ID
            page_size: 每页数量
            page_token: 分页token
            
        Returns:
            成员列表
        """
        logger.info(f"列出群聊成员: {chat_id}")
        
        params = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        
        return await self.api_client.get(
            f"/im/v1/chats/{chat_id}/members",
            params=params
        )
    
    async def add_group_members(
        self,
        chat_id: str,
        user_ids: List[str]
    ) -> bool:
        """
        添加群聊成员
        
        Args:
            chat_id: 群聊ID
            user_ids: 用户ID列表
            
        Returns:
            是否成功
        """
        logger.info(f"添加群聊成员: {chat_id}")
        
        data = {
            "member_id_type": "open_id",
            "member_ids": user_ids
        }
        
        await self.api_client.post(
            f"/im/v1/chats/{chat_id}/members",
            data=data
        )
        
        logger.info(f"✅ 已添加 {len(user_ids)} 个成员")
        return True
    
    async def remove_group_members(
        self,
        chat_id: str,
        user_ids: List[str]
    ) -> bool:
        """
        移除群聊成员
        
        Args:
            chat_id: 群聊ID
            user_ids: 用户ID列表
            
        Returns:
            是否成功
        """
        logger.info(f"移除群聊成员: {chat_id}")
        
        # 构建请求体
        data = {
            "member_id_type": "open_id",
            "member_ids": user_ids
        }
        
        # 调用API - 使用DELETE方法
        await self.api_client.request(
            "DELETE",
            f"/im/v1/chats/{chat_id}/members",
            data=data
        )
        
        logger.info(f"✅ 已移除 {len(user_ids)} 个成员")
        return True


# 便捷函数
async def create_group_chat(
    name: str,
    user_ids: List[str],
    **kwargs
) -> Dict[str, Any]:
    """创建群聊（便捷函数）"""
    token_manager = TokenManager.load_from_config()
    manager = GroupManager(token_manager)
    return await manager.create_group(name, user_ids, **kwargs)


async def get_chat_information(chat_id: str) -> Dict[str, Any]:
    """获取群聊信息（便捷函数）"""
    token_manager = TokenManager.load_from_config()
    manager = GroupManager(token_manager)
    return await manager.get_group_info(chat_id)
