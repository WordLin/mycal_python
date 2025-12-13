"""
示例服务类
"""

from typing import List, Optional
from app.schemas.common import PaginationParams


class ExampleService:
    """示例服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.items = [
            {"id": i, "name": f"Item {i}", "value": i * 10}
            for i in range(1, 101)
        ]
    
    def get_item_by_id(self, item_id: int) -> Optional[dict]:
        """
        根据 ID 获取项目
        
        Args:
            item_id: 项目 ID
            
        Returns:
            项目字典或 None
        """
        for item in self.items:
            if item["id"] == item_id:
                return item
        return None
    
    def get_items(
        self,
        pagination: PaginationParams,
        search: Optional[str] = None
    ) -> dict:
        """
        获取项目列表（带分页和搜索）
        
        Args:
            pagination: 分页参数
            search: 搜索关键词
            
        Returns:
            包含分页信息的字典
        """
        # 搜索过滤
        filtered_items = self.items
        if search:
            filtered_items = [
                item for item in self.items
                if search.lower() in item["name"].lower()
            ]
        
        # 分页计算
        total = len(filtered_items)
        total_pages = (total + pagination.page_size - 1) // pagination.page_size
        start = (pagination.page - 1) * pagination.page_size
        end = start + pagination.page_size
        
        items = filtered_items[start:end]
        
        return {
            "total": total,
            "page": pagination.page,
            "page_size": pagination.page_size,
            "total_pages": total_pages,
            "items": items
        }
    
    def create_item(self, name: str, value: int) -> dict:
        """
        创建新项目
        
        Args:
            name: 项目名称
            value: 项目值
            
        Returns:
            创建的项目字典
        """
        new_id = max([item["id"] for item in self.items], default=0) + 1
        new_item = {"id": new_id, "name": name, "value": value}
        self.items.append(new_item)
        return new_item
    
    def update_item(self, item_id: int, name: Optional[str] = None, value: Optional[int] = None) -> Optional[dict]:
        """
        更新项目
        
        Args:
            item_id: 项目 ID
            name: 新名称（可选）
            value: 新值（可选）
            
        Returns:
            更新后的项目字典或 None
        """
        item = self.get_item_by_id(item_id)
        if not item:
            return None
        
        if name is not None:
            item["name"] = name
        if value is not None:
            item["value"] = value
        
        return item
    
    def delete_item(self, item_id: int) -> bool:
        """
        删除项目
        
        Args:
            item_id: 项目 ID
            
        Returns:
            是否删除成功
        """
        item = self.get_item_by_id(item_id)
        if item:
            self.items.remove(item)
            return True
        return False

