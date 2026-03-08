#!/usr/bin/env python3
"""
Feishu Document Writer - 文档写入器
创建文档、追加内容、智能分块
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List

from ..feishu_common import (
    TokenManager,
    APIClient,
    extract_doc_token_from_url,
)
from .chunker import ContentChunker, ChunkConfig


logger = logging.getLogger(__name__)


class DocumentWriter:
    """文档写入器"""
    
    def __init__(
        self,
        token_manager: TokenManager,
        chunk_config: ChunkConfig = None
    ):
        """
        初始化文档写入器
        
        Args:
            token_manager: Token管理器
            chunk_config: 分块配置
        """
        self.token_manager = token_manager
        self.api_client = APIClient(token_manager)
        self.chunker = ContentChunker(chunk_config)
    
    async def create_document(
        self,
        title: str,
        content: str,
        folder_token: Optional[str] = None,
        owner_openid: Optional[str] = None,
        update_index: bool = False
    ) -> Dict[str, Any]:
        """
        创建文档并写入内容
        
        Args:
            title: 文档标题
            content: 文档内容
            folder_token: 文件夹token（可选）
            owner_openid: 所有者openid（可选，转移所有权）
            update_index: 是否更新索引
            
        Returns:
            {
                "doc_url": "...",
                "doc_token": "...",
                "chunks_count": N,
                "owner_transferred": False,
                "index_updated": False
            }
        """
        logger.info(f"创建文档: {title}")
        
        # 1. 创建空文档
        doc_token = await self._create_empty_doc(title, folder_token)
        doc_url = f"https://feishu.cn/docx/{doc_token}"
        
        logger.info(f"✅ 文档创建成功: {doc_url}")
        
        # 2. 分块写入内容
        chunks = self.chunker.chunk_content(content)
        success = await self._write_chunks(doc_token, chunks)
        
        if not success:
            raise Exception("写入内容失败")
        
        # 3. 转移所有权
        owner_transferred = False
        if owner_openid:
            try:
                from .transfer import OwnershipTransfer
                transfer = OwnershipTransfer(self.token_manager)
                owner_transferred = await transfer.transfer_ownership(doc_url, owner_openid)
                
                if owner_transferred:
                    logger.info(f"✅ 所有权已转移给 {owner_openid}")
            except Exception as e:
                logger.warning(f"转移所有权失败: {e}（不影响文档创建）")
        
        # 4. 更新索引
        index_updated = False
        if update_index:
            try:
                from ..index.manager import IndexManager
                
                # 生成摘要
                summary = content[:100].replace('\n', ' ')
                if len(content) > 100:
                    summary += "..."
                
                # 自动分类
                tags = self._auto_classify(content, title)
                
                # 更新索引
                index_manager = IndexManager()
                index_updated = index_manager.add_doc(
                    name=title,
                    url=doc_url,
                    token=doc_token,
                    summary=summary,
                    tags=tags,
                    owner=owner_openid or ""
                )
                
                if index_updated:
                    logger.info(f"✅ 文档索引已更新")
                
            except Exception as e:
                logger.warning(f"索引更新失败: {e}（不影响文档创建）")
        
        return {
            "doc_url": doc_url,
            "doc_token": doc_token,
            "chunks_count": len(chunks),
            "owner_transferred": owner_transferred,
            "index_updated": index_updated
        }
    
    async def append_document(
        self,
        doc_url: str,
        content: str
    ) -> bool:
        """
        追加内容到文档
        
        Args:
            doc_url: 文档URL
            content: 要追加的内容
            
        Returns:
            是否成功
        """
        logger.info(f"追加内容到: {doc_url}")
        
        # 提取token
        doc_token = extract_doc_token_from_url(doc_url)
        
        # 分块
        chunks = self.chunker.chunk_content(content)
        
        # 写入
        return await self._write_chunks(doc_token, chunks)
    
    async def _create_empty_doc(
        self,
        title: str,
        folder_token: Optional[str] = None
    ) -> str:
        """
        创建空文档
        
        Args:
            title: 文档标题
            folder_token: 文件夹token
            
        Returns:
            doc_token
        """
        # 这里需要调用OpenClaw的feishu_doc工具
        # 由于在Skill中，我们使用ctx.invoke_tool
        # 但在独立脚本中，需要直接调用API
        
        # 先尝试直接调用API
        try:
            return await self._create_doc_via_api(title, folder_token)
        except Exception as e:
            logger.warning(f"API方式创建文档失败: {e}")
            raise Exception(f"创建文档失败，请确保有相应的权限: {e}")
    
    async def _create_doc_via_api(
        self,
        title: str,
        folder_token: Optional[str] = None
    ) -> str:
        """
        通过API创建文档
        
        Args:
            title: 文档标题
            folder_token: 文件夹token
            
        Returns:
            doc_token
        """
        # 注意：这个API可能需要特定的权限
        # 如果失败，建议使用OpenClaw内置的feishu_doc工具
        
        # 构建请求
        data = {
            "title": title,
            "type": "docx"
        }
        
        if folder_token:
            data["folder_token"] = folder_token
        
        # 调用API
        result = await self.api_client.post("/docx/v1/documents", data=data)
        
        # 提取token
        doc_token = result.get("document", {}).get("document_id")
        if not doc_token:
            raise Exception(f"无法解析文档token: {result}")
        
        return doc_token
    
    async def _write_chunks(self, doc_token: str, chunks: List[str]) -> bool:
        """
        分块写入内容
        
        Args:
            doc_token: 文档token
            chunks: 内容分块
            
        Returns:
            是否成功
        """
        logger.info(f"开始写入 {len(chunks)} 块...")
        
        for i, chunk in enumerate(chunks, 1):
            if self.chunker.config.show_progress:
                logger.info(f"  写入第 {i}/{len(chunks)} 块 ({len(chunk)} 字符)...")
            
            # 重试机制
            for attempt in range(self.chunker.config.max_retries):
                try:
                    await self._append_chunk(doc_token, chunk)
                    break
                except Exception as e:
                    if attempt < self.chunker.config.max_retries - 1:
                        delay = self.chunker.config.retry_delay * (attempt + 1)
                        logger.warning(f"    重试 {attempt + 1}/{self.chunker.config.max_retries} 失败，{delay}秒后重试")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"❌ 第 {i} 块写入失败")
                        return False
            
            # Little delay to avoid rate limiting
            if i < len(chunks):
                await asyncio.sleep(0.5)
        
        logger.info(f"✅ 全部 {len(chunks)} 块写入完成")
        return True
    
    async def _append_chunk(self, doc_token: str, chunk: str) -> bool:
        """
        追加单块内容
        
        Args:
            doc_token: 文档token
            chunk: 内容块
            
        Returns:
            是否成功
        """
        # 调用API追加内容
        await self.api_client.post(
            f"/docx/v1/documents/{doc_token}/blocks/doc",
            data={
                "children": [
                    {
                        "paragraph": {
                            "elements": [
                                {
                                    "text_run": {
                                        "content": chunk
                                    }
                                }
                            ]
                        }
                    }
                ],
                "index": -1
            }
        )
        
        return True
    
    def _auto_classify(self, content: str, title: str) -> List[str]:
        """
        根据内容自动分类
        
        Args:
            content: 内容
            title: 标题
            
        Returns:
            标签列表
        """
        tags = []
        text = (title + " " + content).lower()
        
        # 关键词映射到标签
        if any(k in text for k in ["ai", "人工智能", "模型", "gpt", "llm"]):
            tags.append("AI技术")
        
        if any(k in text for k in ["openclaw", "skill", "agent"]):
            tags.append("OpenClaw")
        
        if any(k in text for k in ["飞书", "文档", "feishu", "docx"]):
            tags.append("飞书文档")
        
        if any(k in text for k in ["电商", "tiktok", "alibaba", "玩具"]):
            tags.append("电商")
        
        if any(k in text for k in ["garmin", "strava", "骑行", "健康", "运动"]):
            tags.append("健康运动")
        
        if any(k in text for k in ["对话", "归档", "聊天记录"]):
            tags.append("每日归档")
        
        # 如果没有匹配到特定标签，添加通用标签
        if not tags:
            tags.append("其他")
        
        return tags


# 便捷函数
async def create_feishu_document(
    title: str,
    content: str,
    **kwargs
) -> Dict[str, Any]:
    """
    创建文档（便捷函数）
    
    Args:
        title: 文档标题
        content: 文档内容
        **kwargs: 其他参数
        
    Returns:
        文档信息
    """
    token_manager = TokenManager.load_from_config()
    writer = DocumentWriter(token_manager)
    return await writer.create_document(title, content, **kwargs)


async def append_feishu_document(
    doc_url: str,
    content: str
) -> bool:
    """
    追加内容到文档（便捷函数）
    
    Args:
        doc_url: 文档URL
        content: 要追加的内容
        
    Returns:
        是否成功
    """
    token_manager = TokenManager.load_from_config()
    writer = DocumentWriter(token_manager)
    return await writer.append_document(doc_url, content)
