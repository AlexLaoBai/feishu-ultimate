#!/usr/bin/env python3
"""
Feishu Common - 公共模块
提供统一的Token管理、API客户端、安全扫描等功能
"""

import json
import os
import time
import re
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TokenManager:
    """飞书Token管理器"""
    
    def __init__(self, app_id: str = None, app_secret: str = None):
        """
        初始化Token管理器
        
        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用Secret
        """
        self.app_id = app_id or os.getenv("FEISHU_APP_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET")
        
        # 缓存文件路径
        self.cache_file = Path.home() / ".openclaw" / "workspace" / "memory" / "feishu_token.json"
        
        # 确保缓存目录存在
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 从缓存加载token
        self._token_cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """从缓存文件加载token"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"加载Token缓存失败: {e}")
        return {}
    
    def _save_cache(self, token: str, expire: int):
        """保存token到缓存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "token": token,
                    "expire": expire
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"保存Token缓存失败: {e}")
    
    async def get_token(self) -> str:
        """
        获取tenant_access_token
        如果缓存未过期，使用缓存；否则重新获取
        
        Returns:
            tenant_access_token
        """
        # 检查缓存是否有效
        if self._token_cache.get("token") and self._token_cache.get("expire"):
            now = int(time.time())
            # 提前60秒刷新，避免临界点
            if self._token_cache["expire"] > now + 60:
                logger.debug("使用缓存的Token")
                return self._token_cache["token"]
        
        # 重新获取token
        return await self._refresh_token()
    
    async def _refresh_token(self) -> str:
        """
        刷新token
        
        Returns:
            新的tenant_access_token
        """
        if not self.app_id or not self.app_secret:
            raise ValueError("缺少FEISHU_APP_ID或FEISHU_APP_SECRET")
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    data = await resp.json()
                    
                    if data.get("code") != 0:
                        raise Exception(f"获取Token失败: {data}")
                    
                    token = data.get("tenant_access_token")
                    expire = data.get("expire", 7200)
                    
                    # 缓存token
                    self._save_cache(token, int(time.time()) + expire)
                    
                    logger.info("Token刷新成功")
                    return token
                    
        except Exception as e:
            logger.error(f"刷新Token失败: {e}")
            raise
    
    @classmethod
    def load_from_config(cls, account_id: str = "default") -> "TokenManager":
        """
        从OpenClaw配置加载Token管理器
        
        Args:
            account_id: 飞书账户ID
            
        Returns:
            TokenManager实例
        """
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"OpenClaw配置文件不存在: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            feishu_config = config.get("channels", {}).get("feishu", {})
            accounts = feishu_config.get("accounts", {})
            account = accounts.get(account_id, {})
            
            app_id = account.get("appId") or feishu_config.get("appId")
            app_secret = account.get("appSecret") or feishu_config.get("appSecret")
            
            if not app_id or not app_secret:
                raise ValueError(f"未找到飞书账户配置: {account_id}")
            
            return cls(app_id, app_secret)
            
        except Exception as e:
            raise Exception(f"从配置加载Token管理器失败: {e}")


class APIClient:
    """飞书API客户端"""
    
    def __init__(self, token_manager: TokenManager):
        """
        初始化API客户端
        
        Args:
            token_manager: Token管理器
        """
        self.token_manager = token_manager
        self.base_url = "https://open.feishu.cn/open-apis"
    
    async def request(
        self,
        method: str,
        path: str,
        data: Dict = None,
        params: Dict = None,
        headers: Dict = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        发送API请求（带重试）
        
        Args:
            method: HTTP方法（GET/POST）
            path: API路径（如 /im/v1/messages）
            data: 请求体（JSON）
            params: URL参数
            headers: 额外请求头
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            
        Returns:
            API响应数据
        """
        url = f"{self.base_url}{path}"
        
        for attempt in range(max_retries):
            try:
                token = await self.token_manager.get_token()
                
                request_headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                if headers:
                    request_headers.update(headers)
                
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method,
                        url,
                        headers=request_headers,
                        json=data,
                        params=params
                    ) as resp:
                        result = await resp.json()
                        
                        if result.get("code") != 0:
                            # Token过期，尝试刷新重试
                            if result.get("code") == 99991663:
                                logger.warning("Token过期，刷新后重试")
                                await self.token_manager._refresh_token()
                                continue
                            
                            raise Exception(f"API错误 {result.get('code')}: {result.get('msg')}")
                        
                        return result.get("data", {})
                        
            except aiohttp.ClientError as e:
                if attempt < max_retries - 1:
                    logger.warning(f"请求失败，{retry_delay}秒后重试: {e}")
                    await aiohttp.sleep(retry_delay * (attempt + 1))
                    continue
                raise Exception(f"请求失败: {e}")
            
            except Exception as e:
                raise
    
    async def get(self, path: str, params: Dict = None) -> Dict[str, Any]:
        """GET请求"""
        return await self.request("GET", path, params=params)
    
    async def post(self, path: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """POST请求"""
        return await self.request("POST", path, data=data, params=params)


class SecurityScanner:
Scanner class for detecting secrets.

    @staticmethod
    def scan_for_secrets(content: str) -> bool:
        """
        扫描内容，检测是否包含敏感信息
        
        Args:
            content: 要扫描的内容
            
        Returns:
            True表示检测到敏感信息，抛出异常
        """
        if not content:
            return False
        
        # 敏感信息模式
        secret_patterns = [
            # Anthropic API Key
            r'sk-ant-api03-[a-zA-Z0-9\-_]{20,}',
            # GitHub Personal Access Token
            r'ghp_[a-zA-Z0-9]{10,}',
            # Slack Bot Token
            r'xox[baprs]-[a-zA-Z0-9]{10,}',
            # Private Keys
            r'-----BEGIN [A-Z]+ PRIVATE KEY-----',
            # AWS Access Key
            r'AKIA[0-9A-Z]{16}',
            # Feishu App Secret (partial)
            r'FEISHU_APP_SECRET\s*[:=]\s*[a-zA-Z0-9\-_]{20,}',
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.error("⛔ SECURITY ALERT: 检测到潜在敏感信息")
                raise Exception("Security Alert: 检测到潜在敏感信息，中止发送以防止泄漏")
        
        return False
    
    @staticmethod
    def sanitize_for_log(content: str, max_length: int = 100) -> str:
        """
        对日志内容进行脱敏处理
        
        Args:
            content: 原始内容
            max_length: 最大长度
            
        Returns:
            脱敏后的内容
        """
        if not content:
            return ""
        
        # 截断
        if len(content) > max_length:
            return content[:max_length] + "..."
        
        return content


def infer_receive_id_type(receive_id: str, explicit: Optional[str] = None) -> str:
    """
    推断receive_id_type
    
    Args:
        receive_id: 接收者ID
        explicit: 显式指定的类型
        
    Returns:
        receive_id_type
    """
    if explicit:
        return explicit
    
    if receive_id.startswith("oc_"):
        return "chat_id"
    elif receive_id.startswith("ou_"):
        return "open_id"
    elif receive_id.startswith("on_"):
        return "user_id"
    elif "@" in receive_id:
        return "email"
    
    return "open_id"


def extract_doc_token_from_url(url: str) -> str:
    """
    从URL中提取doc_token
    
    Args:
        url: 文档URL（如 https://feishu.cn/docx/xxx）
        
    Returns:
        doc_token
    """
    match = re.search(r'docx/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    
    raise ValueError(f"无法从URL提取doc_token: {url}")
