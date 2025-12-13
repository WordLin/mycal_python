"""
待办事项数据模型
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class TodoItem:
    """待办事项类"""
    
    def __init__(
        self,
        id: int,
        title: str,
        start_time: datetime,
        duration_hours: float,
        due_date: datetime,
        completed: bool = False,
        priority: int = 1,
        depends_on: Optional[List[int]] = None,
        final_deadline: Optional[datetime] = None
    ):
        self.id = id
        self.title = title
        self.start_time = start_time  # 计划开始时间
        self.duration_hours = duration_hours  # 任务时长（小时）
        self.end_time = start_time + timedelta(hours=duration_hours)  # 计划结束时间
        self.due_date = due_date  # 截止日期
        self.completed = completed
        self.priority = priority  # 1-5，1为最高优先级
        self.depends_on = depends_on or []  # 依赖的任务ID列表
        self.final_deadline = final_deadline  # 最终截止日期（硬性 deadline）
    
    @property
    def status(self) -> TaskStatus:
        """获取任务状态"""
        if self.completed:
            return TaskStatus.COMPLETED
        elif datetime.now() > self.due_date:
            return TaskStatus.OVERDUE
        else:
            return TaskStatus.PENDING
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_hours": self.duration_hours,
            "due_date": self.due_date.isoformat(),
            "completed": self.completed,
            "priority": self.priority,
            "status": self.status.value,
            "depends_on": self.depends_on,
            "final_deadline": self.final_deadline.isoformat() if self.final_deadline else None
        }


class WorkCalendar:
    """工作日历配置"""
    
    def __init__(
        self,
        work_days=None,
        work_start_hour=9,
        work_end_hour=18,
        holidays=None,
        special_workdays=None
    ):
        # 默认周一到周五为工作日 (0=周一, 4=周五)
        self.work_days = work_days or [0, 1, 2, 3, 4]
        self.work_start_hour = work_start_hour
        self.work_end_hour = work_end_hour
        self.holidays = holidays or set()  # 节假日集合
        self.special_workdays = special_workdays or set()  # 特殊工作日集合
    
    def is_workday(self, date: datetime) -> bool:
        """检查是否为工作日"""
        date_date = date.date()
        
        # 检查是否是特殊工作日（周末但上班）
        if date_date in self.special_workdays:
            return True
        
        # 检查是否是节假日
        if date_date in self.holidays:
            return False
        
        # 检查是否是正常工作日
        return date.weekday() in self.work_days
    
    def is_within_work_hours(self, datetime_val: datetime) -> bool:
        """检查是否在工作时间内"""
        if not self.is_workday(datetime_val):
            return False
        return self.work_start_hour <= datetime_val.hour < self.work_end_hour
    
    def get_next_work_time(self, from_time: datetime, duration_hours: float) -> datetime:
        """获取下一个可用的工作时间点"""
        current = from_time
        remaining_hours = duration_hours
        
        while remaining_hours > 0:
            # 如果当前不是工作日，跳到下一个工作日开始
            if not self.is_workday(current):
                next_day = current + timedelta(days=1)
                current = datetime(next_day.year, next_day.month, next_day.day, self.work_start_hour)
                continue
            
            # 计算当天剩余工作时间
            day_end = datetime(current.year, current.month, current.day, self.work_end_hour)
            
            if current.hour < self.work_start_hour:
                current = datetime(current.year, current.month, current.day, self.work_start_hour)
            
            if current >= day_end:
                # 跳到下一天
                next_day = current + timedelta(days=1)
                current = datetime(next_day.year, next_day.month, next_day.day, self.work_start_hour)
                continue
            
            # 计算当前时间段内可工作的小时数
            available_hours = min((day_end - current).total_seconds() / 3600, remaining_hours)
            
            if available_hours > 0:
                remaining_hours -= available_hours
                if remaining_hours > 0:
                    # 需要继续到下一天
                    next_day = current + timedelta(days=1)
                    current = datetime(next_day.year, next_day.month, next_day.day, self.work_start_hour)
                else:
                    current += timedelta(hours=available_hours)
            else:
                # 跳到下一天
                next_day = current + timedelta(days=1)
                current = datetime(next_day.year, next_day.month, next_day.day, self.work_start_hour)
        
        return current


class TodoScheduler:
    """待办事项调度器"""
    
    def __init__(self, calendar: WorkCalendar = None):
        self.calendar = calendar or WorkCalendar()
        self.tasks: List[TodoItem] = []
        self.next_id = 1
    
    def add_task(
        self,
        title: str,
        start_time: datetime,
        duration_hours: float,
        due_date: datetime,
        priority: int = 1,
        depends_on: List[int] = None,
        final_deadline: datetime = None
    ) -> int:
        """添加新任务"""
        task = TodoItem(
            self.next_id,
            title,
            start_time,
            duration_hours,
            due_date,
            False,
            priority,
            depends_on,
            final_deadline
        )
        self.tasks.append(task)
        self.next_id += 1
        return task.id
    
    def get_task(self, task_id: int) -> Optional[TodoItem]:
        """根据 ID 获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def complete_task(self, task_id: int) -> bool:
        """标记任务为完成"""
        task = self.get_task(task_id)
        if task:
            task.completed = True
            return True
        return False
    
    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        start_time: Optional[datetime] = None,
        duration_hours: Optional[float] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[int] = None,
        depends_on: Optional[List[int]] = None,
        final_deadline: Optional[datetime] = None
    ) -> Optional[TodoItem]:
        """更新任务"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        if title is not None:
            task.title = title
        if start_time is not None:
            task.start_time = start_time
            task.end_time = start_time + timedelta(hours=task.duration_hours)
        if duration_hours is not None:
            task.duration_hours = duration_hours
            task.end_time = task.start_time + timedelta(hours=duration_hours)
        if due_date is not None:
            task.due_date = due_date
        if priority is not None:
            task.priority = priority
        if depends_on is not None:
            task.depends_on = depends_on
        if final_deadline is not None:
            task.final_deadline = final_deadline
        
        return task
    
    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False
    
    def auto_reschedule(self, current_time: datetime) -> int:
        """自动重新调度所有过期未完成的任务"""
        # 按优先级和截止日期排序（优先级高、截止日期早的优先）
        pending_tasks = [t for t in self.tasks if not t.completed]
        pending_tasks.sort(key=lambda x: (x.priority, x.due_date))
        
        rescheduled_count = 0
        
        for task in pending_tasks:
            # 检查任务是否过期或不在工作时间内
            if task.due_date < current_time or not self.calendar.is_within_work_hours(task.start_time):
                # 计算新的开始时间（从当前时间或原计划时间的较晚者开始）
                new_start = max(current_time, task.start_time)
                new_start = self.calendar.get_next_work_time(new_start, task.duration_hours)
                
                # 计算新的截止日期，保持与原计划的相对时间差
                time_diff = task.due_date - task.start_time
                new_due_date = new_start + time_diff
                
                # 如果设置了最终截止日期，不能超过
                if task.final_deadline and new_due_date > task.final_deadline:
                    new_due_date = task.final_deadline
                    # 调整开始时间以确保在最终截止日期前完成
                    new_start = new_due_date - time_diff
                    new_start = max(new_start, self.calendar.get_next_work_time(
                        max(current_time, new_start), task.duration_hours))
                
                task.start_time = new_start
                task.due_date = new_due_date
                task.end_time = new_start + timedelta(hours=task.duration_hours)
                rescheduled_count += 1
        
        return rescheduled_count
    
    def get_tasks_for_date(self, date: datetime) -> List[TodoItem]:
        """获取某天的所有任务"""
        target_date = date.date()
        return [t for t in self.tasks if t.start_time.date() == target_date and not t.completed]
    
    def get_all_tasks(self, completed: Optional[bool] = None) -> List[TodoItem]:
        """获取所有任务"""
        if completed is None:
            return self.tasks
        return [t for t in self.tasks if t.completed == completed]

