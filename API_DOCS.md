# 待办事项 API 文档

基于 FastAPI 的待办事项和日程安排 API，支持任务管理、自动调度和日历配置。

## 快速开始

### 启动服务

```bash
uvicorn main:app --reload
```

或使用 Python 直接运行：

```bash
python -m uvicorn main:app --reload
```

### 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 1. 创建任务

**POST** `/api/v1/todos`

创建新的待办任务。

**请求体：**
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

**参数说明：**
- `title` (必填): 任务标题，1-200 字符
- `start_time` (必填): 计划开始时间，ISO 8601 格式
- `duration_hours` (必填): 任务时长（小时），必须大于 0
- `due_date` (必填): 截止日期，ISO 8601 格式
- `priority` (可选): 优先级，1-5（1 为最高），默认 1
- `depends_on` (可选): 依赖的任务ID列表
- `final_deadline` (可选): 最终截止日期（硬性 deadline）

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

**GET** `/api/v1/todos`

获取所有任务列表。

**查询参数：**
- `completed` (可选): 过滤已完成/未完成任务
  - `true`: 只返回已完成的任务
  - `false`: 只返回未完成的任务
  - 不传: 返回所有任务

**响应示例：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 2,
    "tasks": [...]
  }
}
```

### 3. 获取任务详情

**GET** `/api/v1/todos/{task_id}`

获取指定任务的详细信息。

**路径参数：**
- `task_id`: 任务ID

### 4. 更新任务

**PUT** `/api/v1/todos/{task_id}`

更新任务信息。

**请求体：**
```json
{
  "title": "更新后的任务标题",
  "priority": 1,
  "completed": false
}
```

所有字段都是可选的，只更新提供的字段。

### 5. 删除任务

**DELETE** `/api/v1/todos/{task_id}`

删除指定任务。

### 6. 完成任务

**POST** `/api/v1/todos/{task_id}/complete`

标记任务为已完成。

### 7. 获取指定日期的任务

**GET** `/api/v1/todos/date/{date_str}`

获取指定日期的所有未完成任务。

**路径参数：**
- `date_str`: 日期字符串，格式：`YYYY-MM-DD`

**响应示例：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "date": "2024-01-15",
    "is_workday": true,
    "tasks": [...]
  }
}
```

### 8. 获取日程安排

**GET** `/api/v1/todos/schedule/days`

获取未来几天的日程安排。

**查询参数：**
- `days` (可选): 查看天数，1-30，默认 7
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
      "tasks": [...]
    },
    ...
  ]
}
```

### 9. 自动重新调度

**POST** `/api/v1/todos/reschedule`

自动重新调度所有过期未完成的任务。

**请求体：**
```json
{
  "current_time": "2024-01-15T18:00:00"
}
```

如果不提供 `current_time`，将使用当前时间。

**响应示例：**
```json
{
  "code": 200,
  "message": "重新调度完成",
  "data": {
    "rescheduled_count": 2,
    "current_time": "2024-01-15T18:00:00",
    "message": "已重新调度 2 个任务"
  }
}
```

### 10. 获取日历配置

**GET** `/api/v1/todos/calendar/config`

获取当前工作日历配置。

**响应示例：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "work_days": [0, 1, 2, 3, 4],
    "work_start_hour": 9,
    "work_end_hour": 18,
    "holidays": ["2024-01-01", "2024-02-10"],
    "special_workdays": ["2024-01-28"]
  }
}
```

### 11. 更新日历配置

**PUT** `/api/v1/todos/calendar/config`

更新工作日历配置。

**请求体：**
```json
{
  "work_days": [0, 1, 2, 3, 4],
  "work_start_hour": 9,
  "work_end_hour": 18,
  "holidays": ["2024-01-01", "2024-02-10"],
  "special_workdays": ["2024-01-28"]
}
```

**参数说明：**
- `work_days`: 工作日列表，0=周一，4=周五
- `work_start_hour`: 工作开始时间（小时），0-23
- `work_end_hour`: 工作结束时间（小时），0-23
- `holidays`: 节假日列表，YYYY-MM-DD 格式
- `special_workdays`: 特殊工作日列表（周末调休），YYYY-MM-DD 格式

## 功能特性

### 1. 任务状态

任务有三种状态：
- `pending`: 待处理
- `completed`: 已完成
- `overdue`: 已过期

### 2. 优先级

优先级范围：1-5
- 1: 最高优先级
- 5: 最低优先级

### 3. 自动调度

系统会根据工作日历自动调整过期或非工作时间的任务：
- 自动跳过非工作日
- 自动跳过非工作时间
- 保持任务相对时间差
- 考虑最终截止日期限制

### 4. 工作日历

支持灵活的工作日历配置：
- 自定义工作日
- 设置工作时间
- 配置节假日
- 配置特殊工作日（周末调休）

## 使用示例

### Python 示例

```python
import requests

BASE_URL = "http://localhost:8000/api/v1/todos"

# 创建任务
task_data = {
    "title": "编写项目文档",
    "start_time": "2024-01-15T10:00:00",
    "duration_hours": 2.0,
    "due_date": "2024-01-15T14:00:00",
    "priority": 2
}
response = requests.post(f"{BASE_URL}", json=task_data)
print(response.json())

# 获取所有任务
response = requests.get(f"{BASE_URL}")
print(response.json())

# 获取日程安排
response = requests.get(f"{BASE_URL}/schedule/days?days=7")
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

## 错误处理

所有错误响应都遵循统一格式：

```json
{
  "code": 400,
  "message": "错误描述",
  "errors": {
    "detail": "详细错误信息"
  }
}
```

常见错误码：
- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `422`: 数据验证失败
- `500`: 服务器内部错误

