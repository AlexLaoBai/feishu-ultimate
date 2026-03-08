#!/usr/bin/env python3
"""
Feishu Document Chunker - 文档分块器
将长内容智能分割成多个小块，避免API限制
"""

import re
import logging
from dataclasses import dataclass
from typing import List, Optional


logger = logging.getLogger(__name__)


@dataclass
class ChunkConfig:
    """分块配置"""
    chunk_size: int = 2000          # 每块最大字符数
    max_retries: int = 3            # 最大重试次数
    retry_delay: float = 1.0        # 重试间隔（秒）
    show_progress: bool = True      # 显示进度
    convert_tables: bool = True     # 转换表格为文本


class ContentChunker:
    """内容分块器"""
    
    def __init__(self, config: ChunkConfig = None):
        """
        初始化分块器
        
        Args:
            config: 分块配置
        """
        self.config = config or ChunkConfig()
    
    def chunk_content(self, content: str) -> List[str]:
        """
        将长内容分割成多个小块
        
        Args:
            content: 原始内容
            
        Returns:
            分块列表
        """
        chunks = []
        current_chunk = ""
        
        # 先处理表格
        if self.config.convert_tables:
            content = self._convert_tables(content)
        
        # 按段落分割
        paragraphs = self._split_paragraphs(content)
        
        for para in paragraphs:
            # 如果当前块加上新段落会超限
            if len(current_chunk) + len(para) > self.config.chunk_size:
                # 保存当前块
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # 如果单个段落就超限，需要进一步分割
                if len(para) > self.config.chunk_size:
                    sub_chunks = self._split_large_paragraph(para)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # 保存最后一块
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        if self.config.show_progress:
            logger.info(f"内容已分割为 {len(chunks)} 块")
        
        return chunks
    
    def _convert_tables(self, content: str) -> str:
        """
        将Markdown表格转换为文本列表
        
        Args:
            content: 原始内容
            
        Returns:
            转换后的内容
        """
        table_pattern = r'\|[^\n]+\|\n\|[-:| ]+\|\n((?:\|[^\n]+\|\n)+)'
        
        def convert_table(match):
            table_text = match.group(0)
            lines = table_text.strip().split('\n')
            
            # 提取表头
            header = [cell.strip() for cell in lines[0].split('|')[1:-1]]
            
            # 提取数据行
            result = ["【表格内容】"]
            for line in lines[2:]:  # 跳过表头和分隔线
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if cells and any(cells):  # 确保不是空行
                    row_text = ", ".join([f"{h}: {c}" for h, c in zip(header, cells)])
                    result.append(f"- {row_text}")
            
            return "\n".join(result)
        
        return re.sub(table_pattern, convert_table, content)
    
    def _split_paragraphs(self, content: str) -> List[str]:
        """
        按段落分割，保留标题结构
        
        Args:
            content: 原始内容
            
        Returns:
            段落列表
        """
        lines = content.split('\n')
        paragraphs = []
        current_para = ""
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                # 空行，保存当前段落
                if current_para.strip():
                    paragraphs.append(current_para.strip())
                    current_para = ""
                continue
            
            # 如果是标题，单独成段
            if stripped.startswith('#'):
                if current_para.strip():
                    paragraphs.append(current_para.strip())
                    current_para = ""
                paragraphs.append(stripped)
            else:
                current_para += line + "\n"
        
        # 保存最后一段
        if current_para.strip():
            paragraphs.append(current_para.strip())
        
        return paragraphs
    
    def _split_large_paragraph(self, para: str) -> List[str]:
        """
        分割大段落（按句子）
        
        Args:
            para: 大段落
            
        Returns:
            分割后的块列表
        """
        chunks = []
        
        # 按句子分割（支持中英文标点）
        sentences = re.split(r'([。！？.\n])', para)
        current = ""
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                sentence += sentences[i + 1]  # 加上标点
            
            if len(current) + len(sentence) > self.config.chunk_size:
                if current.strip():
                    chunks.append(current.strip())
                current = sentence
            else:
                current += sentence
        
        # 保存最后一块
        if current.strip():
            chunks.append(current.strip())
        
        return chunks


# 便捷函数
def chunk_text(content: str, chunk_size: int = 2000) -> List[str]:
    """
    分块文本（便捷函数）
    
    Args:
        content: 原始内容
        chunk_size: 每块最大字符数
        
    Returns:
        分块列表
    """
    config = ChunkConfig(chunk_size=chunk_size)
    chunker = ContentChunker(config)
    return chunker.chunk_content(content)
