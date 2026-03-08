#!/usr/bin/env python3
"""
Feishu Index Manager - 索引管理模块
自动索引、搜索、列出文档
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any


logger = logging.getLogger(__name__)


class IndexManager:
    """索引管理器"""
    
    def __init__(self, index_file: Optional[Path] = None):
        """
        初始化索引管理器
        
        Args:
            index_file: 索引文件路径
        """
        if index_file:
            self.index_file = index_file
        else:
            self.index_file = (
                Path.home() / ".openclaw" / "workspace" / "memory" / "feishu-docs-index.md"
            )
        
        # 确保目录存在
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
    
    def add_doc(
        self,
        name: str,
        url: str,
        token: str,
        summary: str = "",
        tags: Optional[List[str]] = None,
        owner: str = "",
        status: str = "Completed"
    ) -> bool:
        """
        添加文档到索引
        
        Args:
            name: 文档名称
            url: 文档链接
            token: 文档token
            summary: 摘要
            tags: 标签列表
            owner: 所有者
            status: 状态
            
        Returns:
            是否成功
        """
        logger.info(f"添加文档到索引: {name}")
        
        # 读取现有索引
        docs = self._read_index()
        
        # 检查是否已存在
        for doc in docs:
            if doc.get("token") == token:
                logger.warning(f"文档已存在: {name}")
                # 更新
                doc["name"] = name
                doc["url"] = url
                doc["summary"] = summary
                doc["tags"] = tags or []
                doc["owner"] = owner
                doc["status"] = status
                return self._write_index(docs)
        
        # 添加新文档
        docs.append({
            "name": name,
            "link": url,
            "token": token,
            "summary": summary,
            "tags": tags or [],
            "owner": owner,
            "status": status
        })
        
        return self._write_index(docs)
    
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        搜索文档
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的文档列表
        """
        logger.info(f"搜索文档: {keyword}")
        
        docs = self._read_index()
        keyword_lower = keyword.lower()
        
        results = []
        for doc in docs:
            # 搜索名称、摘要、标签
            name_match = keyword_lower in doc.get("name", "").lower()
            summary_match = keyword_lower in doc.get("summary", "").lower()
            tags_match = any(
                keyword_lower in tag.lower()
                for tag in doc.get("tags", [])
            )
            
            if name_match or summary_match or tags_match:
                results.append(doc)
        
        logger.info(f"找到 {len(results)} 个匹配文档")
        return results
    
    def list_docs(
        self,
        tag: Optional[str] = None,
        status: Optional[str] = None,
        owner: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        列出文档
        
        Args:
            tag: 标签筛选
            status: 状态筛选
            owner: 所有者筛选
            
        Returns:
            文档列表
        """
        logger.info(f"列出文档 (tag={tag}, status={status}, owner={owner})")
        
        docs = self._read_index()
        
        results = []
        for doc in docs:
            # 标签筛选
            if tag and tag not in doc.get("tags", []):
                continue
            
            # 状态筛选
            if status and doc.get("status") != status:
                continue
            
            # 所有者筛选
            if owner and doc.get("owner") != owner:
                continue
            
            results.append(doc)
        
        logger.info(f"找到 {len(results)} 个文档")
        return results
    
    def remove_doc(self, token: str) -> bool:
        """
        从索引中移除文档
        
        Args:
            token: 文档token
            
        Returns:
            是否成功
        """
        logger.info(f"从索引移除文档: {token}")
        
        docs = self._read_index()
        
        # 查找并移除
        new_docs = [doc for doc in docs if doc.get("token") != token]
        
        if len(new_docs) == len(docs):
            logger.warning(f"文档未找到: {token}")
            return False
        
        return self._write_index(new_docs)
    
    def _read_index(self) -> List[Dict[str, Any]]:
        """
        读取索引
        
        Returns:
            文档列表
        """
        if not self.index_file.exists():
            return []
        
        try:
            # 尝试读取JSON格式
            with open(self.index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试解析JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass
            
            # 尝试解析Markdown表格
            return self._parse_markdown_table(content)
            
        except Exception as e:
            logger.warning(f"读取索引失败: {e}")
            return []
    
    def _write_index(self, docs: List[Dict[str, Any]]) -> bool:
        """
        写入索引
        
        Args:
            docs: 文档列表
            
        Returns:
            是否成功
        """
        try:
            # 写入JSON格式
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
            
            logger.info(f"索引已更新: {len(docs)} 个文档")
            return True
            
        except Exception as e:
            logger.error(f"写入索引失败: {e}")
            return False
    
    def _parse_markdown_table(self, content: str) -> List[Dict[str, Any]]:
        """
        解析Markdown表格格式的索引（向后兼容）
        
        Args:
            content: Markdown内容
            
        Returns:
            文档列表
        """
        docs = []
        lines = content.strip().split('\n')
        
        # 查找表格开始
        header_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('|') and '名称' in line:
                header_idx = i
                break
        
        if header_idx < 0:
            return docs
        
        # 解析表头
        headers = [h.strip() for h in lines[header_idx].split('|')[1:-1]]
        
        # 跳过表头分隔线
        data_start = header_idx + 2
        
        # 解析数据行
        for line in lines[data_start:]:
            if not line.strip() or not line.strip().startswith('|'):
                continue
            
            cells = [c.strip() for c in line.split('|')[1:-1]]
            
            if len(cells) >= len(headers):
                doc = {}
                for j, header in enumerate(headers):
                    if j < len(cells):
                        value = cells[j]
                        
                        # 处理特殊字段
                        if header in ["tags"]:
                            doc[header] = [t.strip() for t in value.split(',') if t.strip()]
                        else:
                            doc[header] = value
                
                if doc.get("name"):
                    docs.append(doc)
        
        return docs
    
    def export_to_markdown(self) -> str:
        """
        导出为Markdown表格格式
        
        Returns:
            Markdown格式的索引
        """
        docs = self._read_index()
        
        if not docs:
            return "# 飞书文档索引\n\n暂无文档"
        
        # 构建表头
        lines = [
            "# 飞书文档索引\n",
            f"\n共 {len(docs)} 个文档\n",
            "\n| 序号 | 名称 | 类型 | 链接 | 摘要 | 状态 | 标签 | 所有者 |",
            "|:---:|:---|:---:|:---|:---|:---:|:---|:---|"
        ]
        
        # 添加数据行
        for i, doc in enumerate(docs, 1):
            name = doc.get("name", "")
            link = doc.get("link", "")
            summary = doc.get("summary", "")[:50]
            status = doc.get("status", "")
            tags = ", ".join(doc.get("tags", []))
            owner = doc.get("owner", "")
            
            lines.append(
                f"| {i} | {name} | docx | {link} | {summary} | {status} | {tags} | {owner} |"
            )
        
        return "\n".join(lines)


# 便捷函数
def search_documents(keyword: str) -> List[Dict[str, Any]]:
    """搜索文档（便捷函数）"""
    manager = IndexManager()
    return manager.search(keyword)


def list_all_documents(**kwargs) -> List[Dict[str, Any]]:
    """列出文档（便捷函数）"""
    manager = IndexManager()
    return manager.list_docs(**kwargs)
