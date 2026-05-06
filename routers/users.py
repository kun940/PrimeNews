from fastapi import APIRouter,Depends,HTTPException,status
from config.database_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from models.users_models import User
from schemas.users import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, UserChangePasswordRequest
from crud import users
from utils.auth import get_current_user
from utils.response import success_response
router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(user_data:UserRequest,db:AsyncSession=Depends(get_db)):
    #查询验证用户是否已存在数据库
    existing_user=await users.get_users_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=400,detail="用户已存在")
    #不存在则创建用户
    user=await users.create_user(db, user_data)
    #生成token
    token=await users.create_token(db, user.id)
    #返回响应
    response_data=UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))#把 user 这个字典 / 对象校验并转换成 UserInfoResponse 模型实例)
    return success_response(message="注册成功",data=response_data)

@router.post("/login")
async def login(user_data:UserRequest,db:AsyncSession=Depends(get_db)):
     #先验证用户是否存在以及密码是否正确
    user=await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
         raise HTTPException(status_code=401,detail="用户名或密码错误")
     #生成token
    token=await users.create_token(db, user.id)
     #返回响应
    response_data=UserAuthResponse(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功",data=response_data)

@router.get("/info")
async def get_user_info(user: User=Depends(get_current_user)):
    return success_response(message="获取用户信息成功",data=UserInfoResponse.model_validate(user))

@router.put("/update")
async def update_user_info(user_data:UserUpdateRequest,user: User=Depends(get_current_user),
                           db:AsyncSession=Depends(get_db)):
    user=await users.update_user(db, user.username, user_data)
    return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(user))

@router.put("/password")
async def update_password(
        password_data:UserChangePasswordRequest,
        user: User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    res_change_pwd=await users.change_password(db,user,password_data.old_password,password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="修改密码失败")
    return success_response(message="修改密码成功")