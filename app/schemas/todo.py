"""
待办事项相关的 Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.todo import TaskStatus


class TaskCreate(BaseModel):
    """创建任务请求模型"""
    title: str = Field(..., description="任务标题", min_length=1, max_length=200)
    start_time: datetime = Field(..., description="计划开始时间")
    duration_hours: float = Field(..., gt=0, description="任务时长（小时）")
    due_date: datetime = Field(..., description="截止日期")
    priority: int = Field(default=1, ge=1, le=5, description="优先级（1-5，1为最高）")
    depends_on: Optional[List[int]] = Field(default=None, description="依赖的任务ID列表")
    final_deadline: Optional[datetime] = Field(default=None, description="最终截止日期（硬性 deadline）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "编写项目文档",
                "start_time": "2024-01-15T10:00:00",
                "duration_hours": 2.0,
                "due_date": "2024-01-15T14:00:00",
                "priority": 2,
                "depends_on": [],
                "final_deadline": None
            }
        }


class TaskUpdate(BaseModel):
    """更新任务请求模型"""
    title: Optional[str] = Field(None, description="任务标题", min_length=1, max_length=200)
    start_time: Optional[datetime] = Field(None, description="计划开始时间")
    duration_hours: Optional[float] = Field(None, gt=0, description="任务时长（小时）")
    due_date: Optional[datetime] = Field(None, description="截止日期")
    priority: Optional[int] = Field(None, ge=1, le=5, description="优先级（1-5，1为最高）")
    depends_on: Optional[List[int]] = Field(None, description="依赖的任务ID列表")
    final_deadline: Optional[datetime] = Field(None, description="最终截止日期")
    completed: Optional[bool] = Field(None, description="是否完成")


class TaskResponse(BaseModel):
    """任务响应模型"""
    id: int
    title: str
    start_time: datetime
    end_time: datetime
    duration_hours: float
    due_date: datetime
    completed: bool
    priority: int
    status: str
    depends_on: List[int]
    final_deadline: Optional[datetime]
    
    class Config:
        from_attributes = True


class CalendarConfig(BaseModel):
    """工作日历配置模型"""
    work_days: List[int] = Field(default=[0, 1, 2, 3, 4], description="工作日（0=周一，4=周五）")
    work_start_hour: int = Field(default=9, ge=0, le=23, description="工作开始时间（小时）")
    work_end_hour: int = Field(default=18, ge=0, le=23, description="工作结束时间（小时）")
    holidays: Optional[List[str]] = Field(default=None, description="节假日列表（YYYY-MM-DD格式）")
    special_workdays: Optional[List[str]] = Field(default=None, description="特殊工作日列表（YYYY-MM-DD格式）")


class RescheduleRequest(BaseModel):
    """重新调度请求模型"""
    current_time: Optional[datetime] = Field(default=None, description="当前时间，默认为现在")


class ScheduleResponse(BaseModel):
    """日程响应模型"""
    date: str
    is_workday: bool
    tasks: List[TaskResponse]


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    total: int
    tasks: List[TaskResponse]

