"""分块结果合并工具 - 用于合并多个文本块的总结和标签结果"""
from collections import Counter
from typing import List


def merge_summaries(chunk_summaries: List[str]) -> str:
    """
    合并多个分块总结为一个完整文本

    将各段总结用分隔符连接，便于后续交给AI进行合并精炼

    Args:
        chunk_summaries: 各分块的总结文本列表

    Returns:
        合并后的总结文本
    """
    # 过滤空白总结
    valid_summaries = [s.strip() for s in chunk_summaries if s.strip()]
    if not valid_summaries:
        return ""

    # 用编号和分隔符连接各段总结
    parts = []
    for i, summary in enumerate(valid_summaries, 1):
        parts.append(f"【第{i}段】{summary}")

    return "\n\n".join(parts)


def merge_tags(chunk_tag_lists: List[List[str]]) -> List[str]:
    """
    合并多个分块的标签列表，去重并按频率排序

    出现频率越高的标签排在越前面，保留所有不重复的标签

    Args:
        chunk_tag_lists: 各分块的标签列表

    Returns:
        去重并排序后的标签列表
    """
    # 统计每个标签出现的次数（先标准化名称）
    tag_counter: Counter = Counter()
    for tag_list in chunk_tag_lists:
        normalized = deduplicate_tags(tag_list)
        for tag in normalized:
            tag_counter[tag] += 1

    # 按出现频率降序排列
    sorted_tags = [tag for tag, _ in tag_counter.most_common()]
    return sorted_tags


def deduplicate_tags(tags: List[str]) -> List[str]:
    """
    去重并标准化标签名称

    处理逻辑：
    1. 去除首尾空白
    2. 统一为小写比较（保留原始大小写）
    3. 去除完全重复的标签

    Args:
        tags: 原始标签列表

    Returns:
        去重后的标签列表
    """
    seen: set = set()
    result: List[str] = []

    for tag in tags:
        # 去除首尾空白
        cleaned = tag.strip()
        if not cleaned:
            continue

        # 使用小写形式作为去重依据
        key = cleaned.lower()
        if key not in seen:
            seen.add(key)
            result.append(cleaned)

    return result
