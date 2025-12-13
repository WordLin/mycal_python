"""
待办事项服务层
"""

from datetime import datetime, timedelta
from typing import List, Optional
from app.models.todo import TodoScheduler, WorkCalendar, TodoItem
from app.schemas.todo import TaskCreate, TaskUpdate, CalendarConfig


class TodoService:
    """待办事项服务类"""
    
    def __init__(self):
        """初始化服务，创建调度器实例"""
        self.scheduler = TodoScheduler()
    
    def set_calendar_config(self, config: CalendarConfig) -> dict:
        """
        设置工作日历配置
        
        Args:
            config: 日历配置
            
        Returns:
            配置结果
        """
        holidays = set()
        if config.holidays:
            for holiday_str in config.holidays:
                holidays.add(datetime.strptime(holiday_str, "%Y-%m-%d").date())
        
        special_workdays = set()
        if config.special_workdays:
            for workday_str in config.special_workdays:
                special_workdays.add(datetime.strptime(workday_str, "%Y-%m-%d").date())
        
        self.scheduler.calendar = WorkCalendar(
            work_days=config.work_days,
            work_start_hour=config.work_start_hour,
            work_end_hour=config.work_end_hour,
            holidays=holidays,
            special_workdays=special_workdays
        )
        
        return {"message": "日历配置已更新"}
    
    def create_task(self, task_data: TaskCreate) -> dict:
        """
        创建新任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            创建的任务信息
        """
        task_id = self.scheduler.add_task(
            title=task_data.title,
            start_time=task_data.start_time,
            duration_hours=task_data.duration_hours,
            due_date=task_data.due_date,
            priority=task_data.priority,
            depends_on=task_data.depends_on,
            final_deadline=task_data.final_deadline
        )
        
        task = self.scheduler.get_task(task_id)
        return task.to_dict()
    
    def get_task(self, task_id: int) -> Optional[dict]:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息或 None
        """
        task = self.scheduler.get_task(task_id)
        if task:
            return task.to_dict()
        return None
    
    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[dict]:
        """
        更新任务
        
        Args:
            task_id: 任务ID
            task_data: 更新数据
            
        Returns:
            更新后的任务信息或 None
        """
        task = self.scheduler.update_task(
            task_id=task_id,
            title=task_data.title,
            start_time=task_data.start_time,
            duration_hours=task_data.duration_hours,
            due_date=task_data.due_date,
            priority=task_data.priority,
            depends_on=task_data.depends_on,
            final_deadline=task_data.final_deadline
        )
        
        if task and task_data.completed is not None:
            task.completed = task_data.completed
        
        if task:
            return task.to_dict()
        return None
    
    def delete_task(self, task_id: int) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否删除成功
        """
        return self.scheduler.delete_task(task_id)
    
    def complete_task(self, task_id: int) -> bool:
        """
        完成任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功
        """
        return self.scheduler.complete_task(task_id)
    
    def get_all_tasks(self, completed: Optional[bool] = None) -> List[dict]:
        """
        获取所有任务
        
        Args:
            completed: 是否完成（None 表示全部）
            
        Returns:
            任务列表
        """
        tasks = self.scheduler.get_all_tasks(completed=completed)
        return [task.to_dict() for task in tasks]
    
    def get_tasks_for_date(self, date: datetime) -> List[dict]:
        """
        获取某天的任务
        
        Args:
            date: 日期
            
        Returns:
            任务列表
        """
        tasks = self.scheduler.get_tasks_for_date(date)
        return [task.to_dict() for task in tasks]
    
    def get_schedule(self, days: int = 7, start_date: Optional[datetime] = None) -> List[dict]:
        """
        获取未来几天的日程安排
        
        Args:
            days: 天数
            start_date: 开始日期（默认为今天）
            
        Returns:
            日程列表
        """
        if start_date is None:
            start_date = datetime.now()
        
        schedule = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_tasks = self.scheduler.get_tasks_for_date(date)
            
            schedule.append({
                "date": date.strftime("%Y-%m-%d"),
                "is_workday": self.scheduler.calendar.is_workday(date),
                "tasks": [task.to_dict() for task in sorted(date_tasks, key=lambda x: x.start_time)]
            })
        
        return schedule
    
    def auto_reschedule(self, current_time: Optional[datetime] = None) -> dict:
        """
        自动重新调度任务
        
        Args:
            current_time: 当前时间（默认为现在）
            
        Returns:
            调度结果
        """
        if current_time is None:
            current_time = datetime.now()
        
        rescheduled_count = self.scheduler.auto_reschedule(current_time)
        
        return {
            "rescheduled_count": rescheduled_count,
            "current_time": current_time.isoformat(),
            "message": f"已重新调度 {rescheduled_count} 个任务"
        }


# 创建全局服务实例
todo_service = TodoService()

