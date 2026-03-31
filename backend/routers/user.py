"""
用户模块路由（预留）
当前为占位实现，所有接口返回 501 Not Implemented
后续接入认证系统后替换为真实逻辑
"""

from fastapi import APIRouter, HTTPException, status

from backend.schemas.user import UserCreate, UserLogin, UserResponse, UserFavorite

router = APIRouter(prefix="/users", tags=["用户模块（预留）"])


@router.post("/register", response_model=UserResponse, summary="用户注册（预留）")
async def register(data: UserCreate):
    """
    用户注册接口 - 预留
    TODO: 接入认证系统后实现注册逻辑
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="用户注册功能尚未实现，当前为预留接口",
    )


@router.post("/login", summary="用户登录（预留）")
async def login(data: UserLogin):
    """
    用户登录接口 - 预留
    TODO: 接入认证系统后实现登录逻辑，返回 JWT Token
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="用户登录功能尚未实现，当前为预留接口",
    )


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息（预留）")
async def get_current_user_info():
    """
    获取当前登录用户信息 - 预留
    TODO: 从 JWT Token 中解析用户身份
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="获取用户信息功能尚未实现，当前为预留接口",
    )


@router.post("/favorites", status_code=status.HTTP_201_CREATED, summary="收藏小说（预留）")
async def add_favorite(data: UserFavorite):
    """
    收藏小说接口 - 预留
    TODO: 实现用户收藏小说功能
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="收藏功能尚未实现，当前为预留接口",
    )


@router.get("/favorites", summary="获取收藏列表（预留）")
async def list_favorites():
    """
    获取用户收藏的小说列表 - 预留
    TODO: 实现收藏列表查询
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="收藏列表功能尚未实现，当前为预留接口",
    )
