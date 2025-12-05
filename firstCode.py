from datetime import datetime, timedelta
import json
from enum import Enum
from typing import List, Optional


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class TodoItem:
    def __init__(self, id: int, title: str, start_time: datetime, duration_hours: float,
                 due_date: datetime, completed: bool = False, priority: int = 1,
                 depends_on: Optional[List[int]] = None, final_deadline: Optional[datetime] = None):
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
        if self.completed:
            return TaskStatus.COMPLETED
        elif datetime.now() > self.due_date:
            return TaskStatus.OVERDUE
        else:
            return TaskStatus.PENDING

    def __str__(self):
        status_icon = "✓" if self.completed else "⚠" if self.status == TaskStatus.OVERDUE else "○"
        return (f"{self.id}. {self.title} | 开始: {self.start_time.strftime('%m-%d %H:%M')} | "
                f"时长: {self.duration_hours}h | 截止: {self.due_date.strftime('%m-%d %H:%M')} | "
                f"优先级: {self.priority} | {status_icon}")


class WorkCalendar:
    """工作日历配置"""

    def __init__(self, work_days=None, work_start_hour=9, work_end_hour=18,
                 holidays=None, special_workdays=None):
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
                current = datetime(next_day.year, next_day.month, next_day.day,
                                   self.work_start_hour)
                continue

            # 计算当天剩余工作时间
            day_end = datetime(current.year, current.month, current.day, self.work_end_hour)

            if current.hour < self.work_start_hour:
                current = datetime(current.year, current.month, current.day, self.work_start_hour)

            if current >= day_end:
                # 跳到下一天
                next_day = current + timedelta(days=1)
                current = datetime(next_day.year, next_day.month, next_day.day,
                                   self.work_start_hour)
                continue

            # 计算当前时间段内可工作的小时数
            available_hours = min((day_end - current).total_seconds() / 3600, remaining_hours)

            if available_hours > 0:
                remaining_hours -= available_hours
                if remaining_hours > 0:
                    # 需要继续到下一天
                    next_day = current + timedelta(days=1)
                    current = datetime(next_day.year, next_day.month, next_day.day,
                                       self.work_start_hour)
                else:
                    current += timedelta(hours=available_hours)
            else:
                # 跳到下一天
                next_day = current + timedelta(days=1)
                current = datetime(next_day.year, next_day.month, next_day.day,
                                   self.work_start_hour)

        return current


class TodoScheduler:
    """待办事项调度器"""

    def __init__(self, calendar: WorkCalendar = None):
        self.calendar = calendar or WorkCalendar()
        self.tasks = []
        self.next_id = 1

    def add_task(self, title: str, start_time: datetime, duration_hours: float,
                 due_date: datetime, priority: int = 1, depends_on: List[int] = None,
                 final_deadline: datetime = None) -> int:
        """添加新任务"""
        task = TodoItem(self.next_id, title, start_time, duration_hours, due_date,
                        False, priority, depends_on, final_deadline)
        self.tasks.append(task)
        self.next_id += 1
        return task.id

    def complete_task(self, task_id: int):
        """标记任务为完成"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                break

    def auto_reschedule(self, current_time: datetime):
        """自动重新调度所有过期未完成的任务"""
        print(f"\n=== 在 {current_time.strftime('%Y-%m-%d %H:%M')} 进行自动调度 ===")

        # 按优先级和截止日期排序（优先级高、截止日期早的优先）
        pending_tasks = [t for t in self.tasks if not t.completed]
        pending_tasks.sort(key=lambda x: (x.priority, x.due_date))

        rescheduled_count = 0

        for task in pending_tasks:
            # 检查任务是否过期或不在工作时间内
            if (task.due_date < current_time or
                    not self.calendar.is_within_work_hours(task.start_time)):

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

                print(f"任务 '{task.title}' 重新调度:")
                print(f"  从 {task.start_time.strftime('%m-%d %H:%M')} 调整到 {new_start.strftime('%m-%d %H:%M')}")
                print(f"  截止从 {task.due_date.strftime('%m-%d %H:%M')} 调整到 {new_due_date.strftime('%m-%d %H:%M')}")

                task.start_time = new_start
                task.due_date = new_due_date
                task.end_time = new_start + timedelta(hours=task.duration_hours)
                rescheduled_count += 1

        print(f"共重新调度了 {rescheduled_count} 个任务")
        return rescheduled_count

    def get_tasks_for_date(self, date: datetime) -> List[TodoItem]:
        """获取某天的所有任务"""
        target_date = date.date()
        return [t for t in self.tasks if t.start_time.date() == target_date and not t.completed]

    def print_schedule(self, days: int = 7):
        """打印未来几天的日程安排"""
        print(f"\n=== 未来{days}天日程安排 ===")
        current_date = datetime.now().date()

        for i in range(days):
            date = current_date + timedelta(days=i)
            date_tasks = self.get_tasks_for_date(datetime(date.year, date.month, date.day))

            if date_tasks:
                print(
                    f"\n{date.strftime('%Y-%m-%d')} ({'工作日' if self.calendar.is_workday(datetime(date.year, date.month, date.day)) else '非工作日'}):")
                for task in sorted(date_tasks, key=lambda x: x.start_time):
                    print(f"  {task}")
            else:
                print(f"\n{date.strftime('%Y-%m-%d')}: 无安排")


def create_test_calendar():
    """创建测试用的工作日历"""
    # 设置一些测试用的节假日和特殊工作日
    holidays = {
        datetime(2024, 1, 1).date(),  # 元旦
        datetime(2024, 2, 10).date(),  # 春节
        datetime(2024, 2, 11).date(),
    }

    special_workdays = {
        datetime(2024, 1, 28).date(),  # 周末调休上班
    }

    return WorkCalendar(
        work_days=[0, 1, 2, 3, 4],  # 周一到周五
        work_start_hour=9,
        work_end_hour=18,
        holidays=holidays,
        special_workdays=special_workdays
    )


def run_comprehensive_tests():
    """运行全面的测试用例"""
    print("=" * 60)
    print("开始综合测试")
    print("=" * 60)

    # 创建调度器
    calendar = create_test_calendar()
    scheduler = TodoScheduler(calendar)

    # 测试用例1: 基本任务调度
    print("\n📋 测试用例1: 基本任务调度")
    base_time = datetime(2024, 1, 15, 10, 0)  # 周一上午10点
    scheduler.add_task("编写项目文档", base_time, 2, base_time + timedelta(hours=4), 2)
    scheduler.add_task("团队会议", base_time + timedelta(hours=3), 1, base_time + timedelta(hours=5), 1)
    scheduler.print_schedule(3)

    # 测试用例2: 周末任务自动顺延
    print("\n📋 测试用例2: 周末任务处理")
    weekend_task_time = datetime(2024, 1, 20, 14, 0)  # 周六下午2点
    scheduler.add_task("周末加班任务", weekend_task_time, 3, weekend_task_time + timedelta(hours=5), 2)
    scheduler.auto_reschedule(datetime(2024, 1, 20, 9, 0))  # 周六早上检查
    scheduler.print_schedule(5)

    # 测试用例3: 节假日任务处理
    print("\n📋 测试用例3: 节假日任务处理")
    holiday_task_time = datetime(2024, 2, 10, 10, 0)  # 春节
    scheduler.add_task("春节值班", holiday_task_time, 4, holiday_task_time + timedelta(hours=6), 1)
    scheduler.auto_reschedule(datetime(2024, 2, 10, 8, 0))
    scheduler.print_schedule(7)

    # 测试用例4: 任务依赖关系
    print("\n📋 测试用例4: 优先级和最终截止日期")
    high_priority_time = datetime(2024, 1, 16, 9, 0)
    task_id = scheduler.add_task(
        "高优先级紧急任务",
        high_priority_time,
        8,  # 需要一整天
        high_priority_time + timedelta(days=1),
        priority=1,  # 最高优先级
        final_deadline=datetime(2024, 1, 18, 18, 0)  # 硬性截止日期
    )
    scheduler.auto_reschedule(datetime(2024, 1, 16, 17, 0))  # 下午5点检查
    scheduler.print_schedule(5)

    # 测试用例5: 长时间任务跨多天
    print("\n📋 测试用例5: 长时间任务调度")
    long_task_time = datetime(2024, 1, 17, 14, 0)
    scheduler.add_task("大型项目开发", long_task_time, 16, long_task_time + timedelta(days=2), 2)
    scheduler.auto_reschedule(datetime(2024, 1, 17, 9, 0))
    scheduler.print_schedule(5)

    # 测试用例6: 任务完成测试
    print("\n📋 测试用例6: 任务完成状态")
    scheduler.complete_task(1)  # 完成第一个任务
    print("完成任务后的状态:")
    scheduler.print_schedule(3)

    # 测试用例7: 边缘情况 - 非工作时间开始的任务
    print("\n📋 测试用例7: 非工作时间任务")
    evening_task_time = datetime(2024, 1, 18, 20, 0)  # 晚上8点
    scheduler.add_task("晚间工作", evening_task_time, 2, evening_task_time + timedelta(hours=3), 2)
    scheduler.auto_reschedule(datetime(2024, 1, 18, 18, 1))  # 下班后检查
    scheduler.print_schedule(3)


def interactive_demo():
    """交互式演示"""
    print("\n" + "=" * 60)
    print("交互式演示")
    print("=" * 60)

    calendar = create_test_calendar()
    scheduler = TodoScheduler(calendar)

    # 添加一些示例任务
    now = datetime.now()
    scheduler.add_task("晨会", now.replace(hour=9, minute=0), 1, now.replace(hour=10, minute=0), 2)
    scheduler.add_task("项目开发", now.replace(hour=10, minute=0), 4, now.replace(hour=16, minute=0), 1)
    scheduler.add_task("代码审查", now.replace(hour=15, minute=0), 2, now.replace(hour=17, minute=0), 2)

    while True:
        print("\n选项:")
        print("1. 查看日程")
        print("2. 添加任务")
        print("3. 完成任务")
        print("4. 自动调度")
        print("5. 退出")

        choice = input("请选择操作: ").strip()

        if choice == "1":
            days = int(input("查看多少天的日程? (默认7): ") or "7")
            scheduler.print_schedule(days)

        elif choice == "2":
            title = input("任务标题: ")
            start_str = input("开始时间 (YYYY-MM-DD HH:MM): ")
            duration = float(input("任务时长(小时): "))
            due_str = input("截止时间 (YYYY-MM-DD HH:MM): ")
            priority = int(input("优先级 (1-5, 1最高): "))

            start_time = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
            due_date = datetime.strptime(due_str, "%Y-%m-%d %H:%M")

            scheduler.add_task(title, start_time, duration, due_date, priority)
            print("任务添加成功!")

        elif choice == "3":
            task_id = int(input("要完成的任务ID: "))
            scheduler.complete_task(task_id)
            print("任务标记为完成!")

        elif choice == "4":
            current_str = input("当前时间 (YYYY-MM-DD HH:MM) 或回车使用现在: ")
            current_time = datetime.strptime(current_str, "%Y-%m-%d %H:%M") if current_str else datetime.now()
            scheduler.auto_reschedule(current_time)

        elif choice == "5":
            break
        else:
            print("无效选择!")


if __name__ == "__main__":
    # 运行综合测试
    run_comprehensive_tests()

    # 运行交互式演示
    interactive_demo()