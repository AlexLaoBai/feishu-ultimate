#!/usr/bin/env python3
"""
Feishu Document Transfer - 文档所有权转移
转移文档所有权给指定用户
"""

import logging
from typing import Optional

from ..feishu_common import (
    TokenManager,
    APIClient,
    extract_doc_token_from_url,
)


logger = logging.getLogger(__name__)


class OwnershipTransfer:
    """所有权转移器"""
    
    def __init__(self, token_manager: TokenManager):
        """
        初始化所有权转移器
        
        Args:
            token_manager: Token管理器
        """
        self.token_manager = token_manager
        self.api_client = APIClient(token_manager)
    
    async def transfer_ownership(
        self,
        doc_url: str,
        owner_openid: str
    ) -> bool:
        """
        转移文档所有权
        
        Args:
            doc_url: 文档URL
            owner_openid: 新所有者的openid (例如: ou_xxxxxxxx)
            
        Returns:
            是否成功
        """
        logger.info(f"转移文档所有权: {doc_url} → {owner_openid}")
        
        # 提取doc_token
        doc_token = extract_doc_token_from_url(doc_url)
        
        # 构建请求
        url = f"/drive/v1/permissions/{doc_token}/members/transfer_owner"
        data = {
            "member_type": "openid",
            "member_id": owner_openid
        }
        
        params = {
            "type": "docx"
        }
        
        try:
            # 调用API
            await self.api_client.post(
                url,
                data=data,
                params=params
            )
            
            logger.info(f"✅ 文档所有权已转移给 {owner_openid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 所有权转移失败: {e}")
            return False


# 便捷函数
async def transfer_document_ownership(
    doc_url: str,
    owner_openid: str
) -> bool:
    """
    转移文档所有权（便捷函数）
    
    Args:
        doc_url: 文档URL
        owner_openid: 新所有者的openid
        
    Returns:
        是否成功
    """
    token_manager = TokenManager.load_from_config()
    transfer = OwnershipTransfer(token_manager)
    return await transfer.transfer_ownership(doc_url, owner_openid)
