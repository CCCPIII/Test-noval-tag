"""文件工具函数 - 提供文件名清理、路径生成、临时文件清理等功能"""
import os
import re
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def safe_filename(filename: str) -> str:
    """
    清理文件名，移除不安全字符

    保留中文、字母、数字、下划线、连字符和点号，
    其余字符替换为下划线

    Args:
        filename: 原始文件名

    Returns:
        清理后的安全文件名
    """
    if not filename:
        return "unnamed_file"

    # 分离文件名和扩展名
    name, ext = os.path.splitext(filename)

    # 只保留中文、字母、数字、下划线、连字符
    name = re.sub(r"[^\w\u4e00-\u9fff\-]", "_", name)

    # 去除连续下划线
    name = re.sub(r"_+", "_", name).strip("_")

    # 如果清理后为空，使用默认名称
    if not name:
        name = "unnamed_file"

    # 清理扩展名
    ext = re.sub(r"[^\w.]", "", ext)

    return f"{name}{ext}"


def get_upload_path(filename: str, upload_dir: str) -> str:
    """
    生成上传文件的完整路径

    使用日期和UUID确保文件路径唯一

    Args:
        filename: 原始文件名
        upload_dir: 上传根目录

    Returns:
        完整的文件存储路径
    """
    # 清理文件名
    clean_name = safe_filename(filename)

    # 按日期分子目录
    date_dir = datetime.now().strftime("%Y%m%d")

    # 添加UUID前缀避免重名
    unique_name = f"{uuid.uuid4().hex[:8]}_{clean_name}"

    # 拼接完整路径
    full_dir = os.path.join(upload_dir, date_dir)
    ensure_dir(full_dir)

    return os.path.join(full_dir, unique_name)


def cleanup_temp_file(file_path: str) -> None:
    """
    删除临时文件

    如果文件不存在则忽略，删除失败仅记录日志不抛异常

    Args:
        file_path: 要删除的文件路径
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info("已删除临时文件: %s", file_path)
    except OSError as exc:
        logger.warning("删除临时文件失败: %s, 错误: %s", file_path, exc)


def ensure_dir(dir_path: str) -> None:
    """
    确保目录存在，如果不存在则创建

    Args:
        dir_path: 目录路径
    """
    os.makedirs(dir_path, exist_ok=True)
