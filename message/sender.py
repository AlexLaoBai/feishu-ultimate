#!/usr/bin/env python3
"""
Feishu Message Sender - 消息发送模块
发送文本、卡片、音频消息
"""

import json
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any, List

from ..feishu_common import (
    TokenManager,
    APIClient,
    SecurityScanner,
    infer_receive_id_type,
)


logger = logging.getLogger(__name__)


class MessageSender:
    """消息发送器"""
    
    def __init__(self, token_manager: TokenManager):
        """
        初始化消息发送器
        
        Args:
            token_manager: Token管理器
        """
        self.token_manager = token_manager
        self.api_client = APIClient(token_manager)
        self.security = SecurityScanner()
    
    async def send_text(
        self,
        receive_id: str,
        text: str,
        receive_id_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送文本消息
        
        Args:
            receive_id: 接收者ID（user open_id 或 chat_id）
            text: 消息文本
            receive_id_type: 接收者类型（open_id/chat_id，自动推断）
            
        Returns:
            API响应数据
        """
        # 推断ID类型
        receive_id_type = infer_receive_id_type(receive_id, receive_id_type)
        
        # 安全扫描
        SecurityScanner.scan_for_secrets(text)
        
        # 构建消息体
        payload = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": text})
        }
        
        logger.info(f"发送文本消息到 {receive_id} ({len(text)} 字符)")
        
        # 发送消息
        return await self.api_client.post(
            "/im/v1/messages",
            data=payload,
            params={"receive_id_type": receive_id_type}
        )
    
    async def send_card(
        self,
        receive_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        color: str = "blue",
        button_text: Optional[str] = None,
        button_url: Optional[str] = None,
        image_path: Optional[str] = None,
        receive_id_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送交互式卡片
        
        Args:
            receive_id: 接收者ID
            title: 卡片标题
            content: 卡片内容（Markdown）
            color: 头部颜色
            button_text: 按钮文本
            button_url: 按钮链接
            image_path: 图片路径
            receive_id_type: 接收者类型
            
        Returns:
            API响应数据
        """
        # 推断ID类型
        receive_id_type = infer_receive_id_type(receive_id, receive_id_type)
        
        # 构建卡片元素
        elements = []
        
        # 上传图片
        if image_path:
            try:
                image_key = await self._upload_image(image_path)
                elements.append({
                    "tag": "img",
                    "img_key": image_key,
                    "alt": {"tag": "plain_text", "content": "Image"},
                    "mode": "fit_horizontal"
                })
                logger.info(f"图片上传成功: {image_key}")
            except Exception as e:
                logger.warning(f"图片上传失败，仅发送文本: {e}")
        
        # 添加文本内容
        if content:
            # 安全扫描
            SecurityScanner.scan_for_secrets(content)
            
            elements.append({
                "tag": "markdown",
                "content": content
            })
        
        # 添加按钮
        if button_text and button_url:
            elements.append({
                "tag": "action",
                "actions": [{
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": button_text},
                    "type": "primary",
                    "multi_url": {
                        "url": button_url,
                        "pc_url": "",
                        "android_url": "",
                        "ios_url": ""
                    }
                }]
            })
        
        # 构建卡片对象
        card = {
            "config": {"wide_screen_mode": True},
            "elements": elements
        }
        
        # 添加标题和颜色
        if title:
            card["header"] = {
                "title": {"tag": "plain_text", "content": title},
                "template": color
            }
        
        # 构建消息体
        payload = {
            "receive_id": receive_id,
            "msg_type": "interactive",
            "content": json.dumps(card)
        }
        
        logger.info(f"发送卡片到 {receive_id} (元素数: {len(elements)})")
        
        try:
            # 发送卡片
            return await self.api_client.post(
                "/im/v1/messages",
                data=payload,
                params={"receive_id_type": receive_id_type}
            )
        except Exception as e:
            logger.error(f"发送卡片失败: {e}")
            logger.info("尝试回退到纯文本发送...")
            
            # 回退到纯文本
            fallback_text = content or ""
            if title:
                fallback_text = f"【{title}】\n\n{fallback_text}"
            
            return await self.send_text(receive_id, fallback_text, receive_id_type)
    
    async def send_audio(
        self,
        receive_id: str,
        file_path: str,
        duration_ms: Optional[int] = None,
        receive_id_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        发送音频消息
        
        Args:
            receive_id: 接收者ID
            file_path: 音频文件路径
            duration_ms: 音频时长（毫秒，不指定则自动检测）
            receive_id_type: 接收者类型
            
        Returns:
            API响应数据
        """
        # 推断ID类型
        receive_id_type = infer_receive_id_type(receive_id, receive_id_type)
        
        # 检查文件
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"音频文件不存在: {file_path}")
        
        # 检测时长
        if duration_ms is None:
            duration_ms = await self._detect_audio_duration(file_path)
            logger.info(f"检测到音频时长: {duration_ms}ms")
        
        # 上传音频
        logger.info(f"上传音频: {file_path}")
        file_key = await self._upload_audio(file_path, duration_ms)
        
        # 构建消息体
        payload = {
            "receive_id": receive_id,
            "msg_type": "audio",
            "content": json.dumps({"file_key": file_key})
        }
        
        logger.info(f"发送音频消息到 {receive_id}")
        
        return await self.api_client.post(
            "/im/v1/messages",
            data=payload,
            params={"receive_id_type": receive_id_type}
        )
    
    async def _upload_image(self, file_path: str) -> str:
        """
        上传图片到飞书
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            image_key
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"图片文件不存在: {file_path}")
        
        # 读取文件
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # 构建FormData
        token = await self.token_manager.get_token()
        url = "https://open.feishu.cn/open-apis/im/v1/images"
        
        form_data = aiohttp.FormData()
        form_data.add_field('image_type', 'message')
        form_data.add_field('image', file_data, filename=file_path.name)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                data=form_data
            ) as resp:
                data = await resp.json()
                
                if data.get("code") != 0:
                    raise Exception(f"上传图片失败: {data}")
                
                return data["data"]["image_key"]
    
    async def _upload_audio(self, file_path: Path, duration_ms: int) -> str:
        """
        上传音频到飞书
        
        Args:
            file_path: 音频文件路径
            duration_ms: 音频时长（毫秒）
            
        Returns:
            file_key
        """
        # 读取文件
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # 构建FormData
        token = await self.token_manager.get_token()
        url = "https://open.feishu.cn/open-apis/im/v1/files"
        
        form_data = aiohttp.FormData()
        form_data.add_field('file_type', 'opus')
        form_data.add_field('file_name', file_path.name)
        form_data.add_field('duration', str(duration_ms))
        form_data.add_field('file', file_data, filename=file_path.name)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                data=form_data
            ) as resp:
                data = await resp.json()
                
                if data.get("code") != 0:
                    raise Exception(f"上传音频失败: {data}")
                
                return data["data"]["file_key"]
    
    async def _detect_audio_duration(self, file_path: Path) -> int:
        """
        检测音频时长（毫秒）
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            时长（毫秒）
        """
        try:
            # 尝试使用music-metadata库
            from music_metadata import parseFile
            
            metadata = parseFile(file_path)
            if metadata.format.duration:
                return int(metadata.format.duration * 1000)
        except ImportError:
            logger.warning("music-metadata库未安装，使用默认时长1000ms")
        except Exception as e:
            logger.warning(f"检测音频时长失败: {e}，使用默认时长1000ms")
        
        return 1000


# 便捷函数
async def send_text_message(receive_id: str, text: str, **kwargs) -> Dict[str, Any]:
    """发送文本消息（便捷函数）"""
    token_manager = TokenManager.load_from_config()
    sender = MessageSender(token_manager)
    return await sender.send_text(receive_id, text, **kwargs)


async def send_card_message(receive_id: str, **kwargs) -> Dict[str, Any]:
    """发送卡片消息（便捷函数）"""
    token_manager = TokenManager.load_from_config()
    sender = MessageSender(token_manager)
    return await sender.send_card(receive_id, **kwargs)


async def send_audio_message(receive_id: str, file_path: str, **kwargs) -> Dict[str, Any]:
    """发送音频消息（便捷函数）"""
    token_manager = TokenManager.load_from_config()
    sender = MessageSender(token_manager)
    return await sender.send_audio(receive_id, file_path, **kwargs)
