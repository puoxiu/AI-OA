from app.models.user import OAUser

async def get_responder(user: OAUser) -> OAUser | None:
    # 获取审批者
    # 1. 如果是部门leader
    if user.leader_department and user.leader_department.leader == user:
        # 1.1. 如果是董事会
        if user.department.name == '董事会':
            responder = None
        else:
            responder = user.leader_department.manager
    # 2. 如果不是部门leader
    else:
        responder = user.department.leader if user.department else None
    
    return responder