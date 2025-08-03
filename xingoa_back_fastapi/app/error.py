
# 10000~10999 用户模块
# 11000~11999 业务模块
# 12000~12999 ai模块
# 20000 表示成功
# 50000 表示系统内部错误


class ErrorCode:
    SUCCESS = 20000

    LOGIN_ERROR = 10001
    TOKEN_ERROR = 10002
    USER_LOCKED = 10003
    USER_NOT_ACTIVED = 10004

    ABSENT_NOT_FOUND = 11001
    ABSENT_ALREADY_PROCESSED = 11003
    NOT_PERMITTED = 11004
    NOT_FOUND = 11005
    BOOKING_FAILED = 11006
    ROOM_NOT_ACTIVE = 11007
    BOOKING_TIME_CONFLICT = 11008
    INVALID_PARAM = 11009

    USER_OR_EMAIL_EXIST = 12001
    REPEAT_OPERATION = 12002
    STATUS_EXCEPTION = 12003

    SERVER_ERROR = 50000

    # ...其他错误码

ERROR_MESSAGES = {
    ErrorCode.LOGIN_ERROR: "请输入正确的邮箱和密码",
    ErrorCode.TOKEN_ERROR: "请先登录",
    ErrorCode.USER_LOCKED: "该用户已被锁定，请联系管理员！",
    ErrorCode.USER_NOT_ACTIVED: "该用户尚未激活！",

    ErrorCode.ABSENT_NOT_FOUND: "请假请求不存在",
    ErrorCode.ABSENT_ALREADY_PROCESSED: "该请假请求已处理",
    ErrorCode.BOOKING_FAILED: "预订失败, 请检查会议室是否可用或者时间冲突",
    ErrorCode.ROOM_NOT_ACTIVE: "会议室已停用",
    ErrorCode.BOOKING_TIME_CONFLICT: "预订时间冲突",
    
    ErrorCode.INVALID_PARAM: "参数错误",
    ErrorCode.NOT_PERMITTED: "您没有权限执行该操作",
    ErrorCode.USER_OR_EMAIL_EXIST: "用户名或邮箱已存在",
    ErrorCode.REPEAT_OPERATION: "重复操作",
    ErrorCode.STATUS_EXCEPTION: "状态异常",
    ErrorCode.NOT_FOUND: "资源不存在",
    
    ErrorCode.SERVER_ERROR: "系统错误！请联系管理员！",
}
