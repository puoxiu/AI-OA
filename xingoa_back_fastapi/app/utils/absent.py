from app.models.user import OAUser

def get_responder(user: OAUser) -> OAUser | None:
    print("当前用户信息:", user.username)
    print("当前用户部门:", user.leader_department)
    print( user.leader_department.leader)
    print(f"用户是否为部门leader: {user.leader_department and user.leader_department.leader == user}")
    print(f"用户所在部门名称: {user.department.name if user.department else '无部门'}")
    # 获取审批者
    # 如果是部门leader
    if user.leader_department and user.leader_department.leader == user:
        # 如果是董事会
        if user.department.name == '董事会':
            responder = user
        else:
            responder = user.leader_department.manager
    # 2. 如果不是部门leader
    else:
        responder = user.department.leader if user.department else None
    
    return responder