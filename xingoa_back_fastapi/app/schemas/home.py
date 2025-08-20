from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 最新通知响应模型
class LatestInformResponse(BaseModel):
    id: int
    title: str
    author_name: str
    create_time: datetime
    is_read: bool

# 最新考勤响应模型
class LatestAbsentResponse(BaseModel):
    id: int
    requester_name: str  # 申请人姓名
    absent_type_name: str  # 请假类型
    start_date: datetime
    end_date: datetime
    status: int  # 审批状态
    create_time: datetime

# 部门员工数量统计响应模型
class DepartmentStaffCountResponse(BaseModel):
    name: str  # 部门名称
    staff_count: int  # 员工数量