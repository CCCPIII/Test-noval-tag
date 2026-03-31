"""分页工具 - 提供通用的分页参数和响应封装"""
from dataclasses import dataclass, field
from typing import Generic, List, TypeVar, Any

T = TypeVar("T")


@dataclass
class PaginationParams:
    """分页请求参数"""

    page: int = 1         # 当前页码，从1开始
    page_size: int = 20   # 每页数量，默认20

    def __post_init__(self):
        """参数校验和修正"""
        # 页码最小为1
        if self.page < 1:
            self.page = 1
        # 每页数量限制在1-100之间
        if self.page_size < 1:
            self.page_size = 1
        elif self.page_size > 100:
            self.page_size = 100

    @property
    def offset(self) -> int:
        """计算数据库查询偏移量"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """返回每页数量（等同于page_size）"""
        return self.page_size


@dataclass
class PaginatedResponse(Generic[T]):
    """分页响应封装"""

    items: List[T]          # 当前页数据列表
    total: int              # 总记录数
    page: int               # 当前页码
    page_size: int          # 每页数量

    @property
    def total_pages(self) -> int:
        """计算总页数"""
        if self.total <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page > 1

    def to_dict(self) -> dict:
        """转换为字典，便于API响应序列化"""
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }


def paginate_query(query: Any, page: int, page_size: int) -> Any:
    """
    对SQLAlchemy查询对象应用分页

    Args:
        query: SQLAlchemy查询对象
        page: 页码（从1开始）
        page_size: 每页数量

    Returns:
        应用了offset和limit的查询对象
    """
    params = PaginationParams(page=page, page_size=page_size)
    return query.offset(params.offset).limit(params.limit)
