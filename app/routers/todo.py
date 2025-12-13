"""
待办事项路由
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional, List
from datetime import datetime
from app.schemas.todo import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    CalendarConfig,
    RescheduleRequest,
    ScheduleResponse,
    TaskListResponse
)
from app.services.todo_service import todo_service
from app.utils.response import ResponseModel

router = APIRouter(prefix="/api/v1/todos", tags=["待办事项"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate):
    """
    创建新任务
    """
    try:
        task = todo_service.create_task(task_data)
        return ResponseModel.success(
            data=task,
            message="任务创建成功",
            code=status.HTTP_201_CREATED
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建任务失败: {str(e)}"
        )


@router.get("", response_model=dict)
async def get_tasks(
    completed: Optional[bool] = Query(None, description="是否完成（true/false/null表示全部）")
):
    """
    获取所有任务
    """
    tasks = todo_service.get_all_tasks(completed=completed)
    return ResponseModel.success(
        data={
            "total": len(tasks),
            "tasks": tasks
        },
        message="获取成功"
    )


@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: int):
    """
    获取任务详情
    """
    task = todo_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return ResponseModel.success(data=task, message="获取成功")


@router.put("/{task_id}", response_model=dict)
async def update_task(task_id: int, task_data: TaskUpdate):
    """
    更新任务
    """
    task = todo_service.update_task(task_id, task_data)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return ResponseModel.success(data=task, message="更新成功")


@router.delete("/{task_id}", response_model=dict)
async def delete_task(task_id: int):
    """
    删除任务
    """
    success = todo_service.delete_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return ResponseModel.success(message="删除成功")


@router.post("/{task_id}/complete", response_model=dict)
async def complete_task(task_id: int):
    """
    完成任务
    """
    success = todo_service.complete_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return ResponseModel.success(message="任务已完成")


@router.get("/date/{date_str}", response_model=dict)
async def get_tasks_for_date(date_str: str):
    """
    获取指定日期的任务
    
    Args:
        date_str: 日期字符串，格式：YYYY-MM-DD
    """
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        tasks = todo_service.get_tasks_for_date(date)
        return ResponseModel.success(
            data={
                "date": date_str,
                "is_workday": todo_service.scheduler.calendar.is_workday(date),
                "tasks": tasks
            },
            message="获取成功"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="日期格式错误，请使用 YYYY-MM-DD 格式"
        )


@router.get("/schedule/days", response_model=dict)
async def get_schedule(
    days: int = Query(7, ge=1, le=30, description="查看天数"),
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD），默认为今天")
):
    """
    获取未来几天的日程安排
    """
    start = None
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日期格式错误，请使用 YYYY-MM-DD 格式"
            )
    
    schedule = todo_service.get_schedule(days=days, start_date=start)
    return ResponseModel.success(
        data=schedule,
        message="获取成功"
    )


@router.post("/reschedule", response_model=dict)
async def auto_reschedule(request: RescheduleRequest):
    """
    自动重新调度过期未完成的任务
    """
    current_time = request.current_time
    if current_time is None:
        current_time = datetime.now()
    
    result = todo_service.auto_reschedule(current_time)
    return ResponseModel.success(data=result, message="重新调度完成")


@router.put("/calendar/config", response_model=dict)
async def update_calendar_config(config: CalendarConfig):
    """
    更新工作日历配置
    """
    try:
        result = todo_service.set_calendar_config(config)
        return ResponseModel.success(data=result, message="日历配置更新成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"配置更新失败: {str(e)}"
        )


@router.get("/calendar/config", response_model=dict)
async def get_calendar_config():
    """
    获取当前工作日历配置
    """
    calendar = todo_service.scheduler.calendar
    holidays = [d.strftime("%Y-%m-%d") for d in calendar.holidays]
    special_workdays = [d.strftime("%Y-%m-%d") for d in calendar.special_workdays]
    
    return ResponseModel.success(
        data={
            "work_days": calendar.work_days,
            "work_start_hour": calendar.work_start_hour,
            "work_end_hour": calendar.work_end_hour,
            "holidays": holidays,
            "special_workdays": special_workdays
        },
        message="获取成功"
    )

