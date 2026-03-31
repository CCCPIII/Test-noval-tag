"""
文件解析服务
负责解析上传的小说文件（TXT / PDF），提取纯文本内容
"""

import os
import re
import chardet
import fitz  # PyMuPDF


def parse_txt(file_path: str) -> str:
    """
    解析 TXT 文件
    - 使用 chardet 自动检测文件编码
    - 去除 BOM 头
    - 统一换行符为 \n
    """
    # 先以二进制模式读取，用于编码检测
    with open(file_path, "rb") as f:
        raw_data = f.read()

    # 检测编码
    detection = chardet.detect(raw_data)
    encoding = detection.get("encoding", "utf-8") or "utf-8"

    # 解码文本
    text = raw_data.decode(encoding, errors="replace")

    # 去除 BOM（Byte Order Mark）
    if text.startswith("\ufeff"):
        text = text[1:]

    # 统一换行符
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    return text


def parse_pdf(file_path: str) -> str:
    """
    解析 PDF 文件
    使用 PyMuPDF (fitz) 逐页提取文本，拼接为完整内容
    """
    doc = fitz.open(file_path)
    pages_text = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text("text")
        if page_text.strip():
            pages_text.append(page_text)
    doc.close()

    # 用换行符连接各页文本
    return "\n".join(pages_text)


def clean_text(text: str) -> str:
    """
    清洗文本内容
    - 移除多余空白行（超过2个连续空行压缩为2个）
    - 移除行首行尾多余空格
    - 尝试去除常见水印/页眉页脚模式
    """
    # 去除常见水印模式，如 "本书由XXX提供下载" 等
    watermark_patterns = [
        r"本书由.*?提供下载",
        r"更多.*?请访问.*",
        r"www\.\S+\.\S+",
        r"http[s]?://\S+",
    ]
    for pattern in watermark_patterns:
        text = re.sub(pattern, "", text)

    # 移除每行首尾空格
    lines = [line.strip() for line in text.split("\n")]

    # 压缩连续空行：超过2个空行压缩为2个
    cleaned_lines = []
    empty_count = 0
    for line in lines:
        if line == "":
            empty_count += 1
            if empty_count <= 2:
                cleaned_lines.append(line)
        else:
            empty_count = 0
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def parse_file(file_path: str, filename: str) -> tuple:
    """
    根据文件扩展名选择解析器，返回清洗后的文本和字符数

    Args:
        file_path: 文件在服务器上的实际路径
        filename: 原始文件名，用于判断扩展名

    Returns:
        (clean_text, char_count) 清洗后的文本和字符数
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        raw_text = parse_txt(file_path)
    elif ext == ".pdf":
        raw_text = parse_pdf(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}，仅支持 .txt 和 .pdf")

    # 清洗文本
    cleaned = clean_text(raw_text)
    char_count = len(cleaned)

    return cleaned, char_count
