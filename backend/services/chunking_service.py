"""
文本分块服务
将超长小说文本切分为带重叠的块，供 AI 分批处理

分块策略：
1. 优先在章节标记处切分（如 "第X章"、"Chapter X"）
2. 其次在段落边界切分（双换行符）
3. 最后在句号等句子边界切分
4. 相邻块之间保留重叠字符，保证上下文连贯
"""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class TextChunk:
    """文本块数据结构"""
    index: int       # 块序号，从 0 开始
    text: str        # 块文本内容
    start_pos: int   # 在原文中的起始位置
    end_pos: int     # 在原文中的结束位置


# 章节标题正则模式，匹配常见中英文章节标记
CHAPTER_PATTERN = re.compile(
    r"\n(?="
    r"第[零一二三四五六七八九十百千\d]+[章节回卷]"  # 中文章节
    r"|Chapter\s+\d+"                                 # 英文章节
    r"|CHAPTER\s+\d+"                                 # 英文章节（大写）
    r")"
)


def _find_best_split_point(text: str, target_pos: int, search_range: int = 500) -> int:
    """
    在 target_pos 附近寻找最佳切分点

    优先级：章节边界 > 段落边界（双换行） > 句子边界（句号等）

    Args:
        text: 完整文本
        target_pos: 目标切分位置
        search_range: 前后搜索范围

    Returns:
        最佳切分位置
    """
    search_start = max(0, target_pos - search_range)
    search_end = min(len(text), target_pos + search_range)
    search_text = text[search_start:search_end]

    # 优先寻找章节边界
    chapter_matches = list(CHAPTER_PATTERN.finditer(search_text))
    if chapter_matches:
        # 选择最靠近 target_pos 的章节边界
        best = min(chapter_matches, key=lambda m: abs((search_start + m.start()) - target_pos))
        return search_start + best.start() + 1  # +1 跳过换行符

    # 其次寻找段落边界（双换行）
    para_pattern = re.compile(r"\n\n")
    para_matches = list(para_pattern.finditer(search_text))
    if para_matches:
        best = min(para_matches, key=lambda m: abs((search_start + m.start()) - target_pos))
        return search_start + best.end()  # 在双换行之后切分

    # 最后寻找句子边界（中英文句号、问号、感叹号）
    sentence_pattern = re.compile(r"[。！？.!?]+")
    sentence_matches = list(sentence_pattern.finditer(search_text))
    if sentence_matches:
        best = min(sentence_matches, key=lambda m: abs((search_start + m.end()) - target_pos))
        return search_start + best.end()

    # 如果都没找到，直接在 target_pos 处切分
    return target_pos


def chunk_text(
    text: str,
    chunk_size: int = 8000,
    overlap: int = 500,
) -> List[TextChunk]:
    """
    将长文本切分为多个带重叠的文本块

    Args:
        text: 完整的小说文本
        chunk_size: 每个块的目标大小（字符数）
        overlap: 相邻块之间的重叠字符数

    Returns:
        TextChunk 列表，每个包含块索引、文本、起止位置
    """
    text_length = len(text)

    # 文本长度不超过 chunk_size 时，不需要切分
    if text_length <= chunk_size:
        return [TextChunk(index=0, text=text, start_pos=0, end_pos=text_length)]

    chunks: List[TextChunk] = []
    current_pos = 0
    chunk_index = 0

    while current_pos < text_length:
        # 计算当前块的结束位置
        end_pos = current_pos + chunk_size

        if end_pos >= text_length:
            # 最后一个块，直接取到末尾
            chunk_text_content = text[current_pos:]
            chunks.append(TextChunk(
                index=chunk_index,
                text=chunk_text_content,
                start_pos=current_pos,
                end_pos=text_length,
            ))
            break

        # 在目标位置附近寻找最佳切分点
        split_pos = _find_best_split_point(text, end_pos)

        chunk_text_content = text[current_pos:split_pos]
        chunks.append(TextChunk(
            index=chunk_index,
            text=chunk_text_content,
            start_pos=current_pos,
            end_pos=split_pos,
        ))

        # 下一块的起始位置：往回退 overlap 个字符，保证上下文重叠
        current_pos = max(split_pos - overlap, current_pos + 1)
        chunk_index += 1

    return chunks
