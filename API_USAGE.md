# 日程安排 API 使用指南

基于 `firstCode.py` 实现的 FastAPI 接口，用于设置和管理日程安排。

## 快速开始

### 启动服务

```bash
uvicorn main:app --reload
```

访问 API 文档：http://localhost:8000/docs

## API 接口说明

### 1. 创建任务

**POST** `/api/v1/todos`

创建新的待办任务。

**请求体示例：**
```json
{
  "title": "编写项目文档",
  "start_time": "2024-01-15T10:00:00",
  "duration_hours": 2.0,
  "due_date": "2024-01-15T14:00:00",
  "priority": 2,
  "depends_on": [],
  "final_deadline": null
}
```

**响应示例：**
```json
{
  "code": 201,
  "message": "任务创建成功",
  "data": {
    "id": 1,
    "title": "编写项目文档",
    "start_time": "2024-01-15T10:00:00",
    "end_time": "2024-01-15T12:00:00",
    "duration_hours": 2.0,
    "due_date": "2024-01-15T14:00:00",
    "completed": false,
    "priority": 2,
    "status": "pending",
    "depends_on": [],
    "final_deadline": null
  }
}
```

### 2. 获取所有任务

**GET** `/api/v1/todos?completed=false`

获取任务列表，可通过 `completed` 参数过滤。

**查询参数：**
- `completed` (可选): `true`/`false`/`null`（全部）

### 3. 获取任务详情

**GET** `/api/v1/todos/{task_id}`

根据任务 ID 获取任务详情。

### 4. 更新任务

**PUT** `/api/v1/todos/{task_id}`

更新任务信息。

**请求体示例：**
```json
{
  "title": "更新后的任务标题",
  "priority": 1,
  "completed": false
}
```

### 5. 删除任务

**DELETE** `/api/v1/todos/{task_id}`

删除指定任务。

### 6. 完成任务

**POST** `/api/v1/todos/{task_id}/complete`

标记任务为已完成。

### 7. 获取指定日期的任务

**GET** `/api/v1/todos/date/{date_str}`

获取指定日期的所有任务。

**路径参数：**
- `date_str`: 日期字符串，格式：`YYYY-MM-DD`

**示例：** `/api/v1/todos/date/2024-01-15`

### 8. 获取日程安排

**GET** `/api/v1/todos/schedule/days?days=7&start_date=2024-01-15`

获取未来几天的日程安排。

**查询参数：**
- `days` (可选): 查看天数，默认 7 天，范围 1-30
- `start_date` (可选): 开始日期（YYYY-MM-DD），默认为今天

**响应示例：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "date": "2024-01-15",
      "is_workday": true,
      "tasks": [
        {
          "id": 1,
          "title": "编写项目文档",
          "start_time": "2024-01-15T10:00:00",
          ...
        }
      ]
    }
  ]
}
```

### 9. 自动重新调度

**POST** `/api/v1/todos/reschedule`

自动重新调度过期未完成的任务。

**请求体示例：**
```json
{
  "current_time": "2024-01-15T09:00:00"
}
```

如果不提供 `current_time`，将使用当前时间。

### 10. 更新工作日历配置

**PUT** `/api/v1/todos/calendar/config`

设置工作日历配置（工作日、工作时间、节假日等）。

**请求体示例：**
```json
{
  "work_days": [0, 1, 2, 3, 4],
  "work_start_hour": 9,
  "work_end_hour": 18,
  "holidays": ["2024-01-01", "2024-02-10"],
  "special_workdays": ["2024-01-28"]
}
```

### 11. 获取工作日历配置

**GET** `/api/v1/todos/calendar/config`

获取当前的工作日历配置。

## 使用示例

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/todos"

# 创建任务
task_data = {
    "title": "团队会议",
    "start_time": "2024-01-15T14:00:00",
    "duration_hours": 1.0,
    "due_date": "2024-01-15T15:00:00",
    "priority": 1
}

response = requests.post(f"{BASE_URL}", json=task_data)
print(response.json())

# 获取未来7天的日程
response = requests.get(f"{BASE_URL}/schedule/days?days=7")
print(response.json())

# 自动重新调度
response = requests.post(f"{BASE_URL}/reschedule", json={})
print(response.json())
```

### cURL 示例

```bash
# 创建任务
curl -X POST "http://localhost:8000/api/v1/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "编写项目文档",
    "start_time": "2024-01-15T10:00:00",
    "duration_hours": 2.0,
    "due_date": "2024-01-15T14:00:00",
    "priority": 2
  }'

# 获取所有任务
curl "http://localhost:8000/api/v1/todos"

# 获取日程安排
curl "http://localhost:8000/api/v1/todos/schedule/days?days=7"
```

## 功能特性

- ✅ 任务创建、更新、删除、完成
- ✅ 工作日历配置（工作日、工作时间、节假日）
- ✅ 自动任务调度（考虑工作日和节假日）
- ✅ 任务优先级管理
- ✅ 任务依赖关系
- ✅ 最终截止日期（硬性 deadline）
- ✅ 按日期查询任务
- ✅ 日程安排查看

## 注意事项

1. 所有时间字段使用 ISO 8601 格式：`YYYY-MM-DDTHH:MM:SS`
2. 优先级范围：1-5，1 为最高优先级
3. 工作日配置：0=周一，1=周二，...，4=周五
4. 任务状态自动计算：pending（待办）、completed（已完成）、overdue（已过期）

