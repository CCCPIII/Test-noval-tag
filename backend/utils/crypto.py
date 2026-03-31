"""加密工具 - 用于API Key等敏感信息的加解密"""
import base64
import hashlib

from cryptography.fernet import Fernet


def _derive_fernet_key(encryption_key: str) -> bytes:
    """
    从任意字符串派生一个合法的Fernet密钥

    Fernet要求32字节的url-safe base64编码密钥，
    这里使用SHA-256哈希将任意长度密钥转为固定长度

    Args:
        encryption_key: 用户提供的加密密钥字符串

    Returns:
        Fernet兼容的密钥字节串
    """
    # 使用SHA-256生成32字节哈希
    digest = hashlib.sha256(encryption_key.encode("utf-8")).digest()
    # 转为url-safe base64编码（Fernet要求的格式）
    return base64.urlsafe_b64encode(digest)


def encrypt_api_key(plain_key: str, encryption_key: str) -> str:
    """
    使用AES加密API Key

    Args:
        plain_key: 明文API Key
        encryption_key: 加密密钥

    Returns:
        Base64编码的加密字符串
    """
    fernet_key = _derive_fernet_key(encryption_key)
    fernet = Fernet(fernet_key)
    encrypted = fernet.encrypt(plain_key.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_api_key(encrypted_key: str, encryption_key: str) -> str:
    """
    解密API Key

    Args:
        encrypted_key: 加密后的API Key字符串
        encryption_key: 加密密钥（需与加密时相同）

    Returns:
        解密后的明文API Key
    """
    fernet_key = _derive_fernet_key(encryption_key)
    fernet = Fernet(fernet_key)
    decrypted = fernet.decrypt(encrypted_key.encode("utf-8"))
    return decrypted.decode("utf-8")
