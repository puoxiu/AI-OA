# AI-OA/xingoa_back_fastapi/app/api/v1/absent.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.absent import AbsentCreateResponse, AbsentCreateRequest, AbsentUpdate
from app.services.absent import AbsentService
from deps.deps import get_db_session
from app.core.auth import AuthTokenHelper
from app.models.user import OAUser
from app.services.auth import UserService
from app.utils.absent import get_responder

router = APIRouter(
    prefix="/api/v1/absent",
    tags=["考勤管理"]
)


@router.post("/", response_model=AbsentCreateResponse)
async def create_new_absent(
    absent: AbsentCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    token: str = Depends(AuthTokenHelper.get_token)
):
    """
    发出请假
    """
    payload = AuthTokenHelper.token_decode(token)
    if not payload:
        raise HTTPException(status_code=401, detail="请先登录！")
    
    email = payload.get("email")
    user = await UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=400, detail="用户不存在")
    
    # 这里需要实现获取审批者的逻辑? await?
    responder = await get_responder(user)

    new_absent = await AbsentService.create_absent(db, absent, user.uid, responder.uid)
    return new_absent


# @router.get("/", response_model=list[AbsentCreateResponse])
# async def get_all_absents(
#     who: str = None,
#     db: AsyncSession = Depends(get_db_session),
#     token: str = Depends(AuthTokenHelper.get_token)
# ):
#     payload = AuthTokenHelper.token_decode(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="无效的令牌")
#     email = payload.get("email")
#     user = await UserService.get_user_by_email(db, email)
#     if not user:
#         raise HTTPException(status_code=400, detail="用户不存在")
#     if who and who == 'sub':
#         absents = await get_absents(db, responder_id=user.uid)
#     else:
#         absents = await get_absents(db, requester_id=user.uid)
#     return absents

# @router.put("/{absent_id}", response_model=AbsentSerializer)
# async def update_absent_info(
#     absent_id: int,
#     absent_update: AbsentUpdate,
#     db: AsyncSession = Depends(get_db_session),
#     token: str = Depends(AuthTokenHelper.get_token)
# ):
#     payload = AuthTokenHelper.token_decode(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="无效的令牌")
#     email = payload.get("email")
#     user = await UserService.get_user_by_email(db, email)
#     if not user:
#         raise HTTPException(status_code=400, detail="用户不存在")
#     absent = await get_absent_by_id(db, absent_id)
#     if not absent:
#         raise HTTPException(status_code=404, detail="考勤记录不存在")
#     if absent.responder_id != user.uid:
#         raise HTTPException(status_code=403, detail="您无权处理该考勤！")
#     updated_absent = await update_absent(db, absent_id, absent_update)
#     return updated_absent