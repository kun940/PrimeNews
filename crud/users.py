import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from models.users_models import User,UserToken
from sqlalchemy import select, func, update
from schemas.users import UserRequest, UserUpdateRequest
from utils import security
#根据用户名查询数据库
async def get_users_by_username(db:AsyncSession,username:str):
    query=select(User).where(User.username==username)
    result=await db.execute(query)
    return result.scalar_one_or_none()

#创建用户到数据库中
async def create_user(db:AsyncSession,user_data:UserRequest):
    #先对密码加密处理
    hashed_password=security.get_hash_password(user_data.password)

    user=User(username=user_data.username, password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)#从数据库读回最新的user
    return user

#生成用户token
async def create_token(db:AsyncSession,user_id:int):
    #先生成一个新token以及过期时间
    token=str(uuid.uuid4())
    expires_at=datetime.now()+timedelta(days=7)
    #查询token表中有无该用户的token
    query=select(UserToken).where(UserToken.user_id==user_id)
    result=await db.execute(query)
    user_token=result.scalar_one_or_none()
    #有则更新token
    if user_token:
        user_token.token=token
        user_token.expires_at=expires_at
    #无则增加
    else:
        user_token=UserToken(user_id=user_id,token=token,expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token

#登录校验用户信息
async def authenticate_user(db:AsyncSession,user_name:str,password:str):
    user=await get_users_by_username(db,user_name)
    if not user:
        return None
    if not security.verify_password(password,user.password):
        return None
    return user

#根据token查用户
async def get_user_by_token(db:AsyncSession,token:str):
    query=select(UserToken).where(UserToken.token==token)
    result=await db.execute(query)
    db_token=result.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now():
        return None
    query=select(User).where(User.id==db_token.user_id)
    result=await db.execute(query)
    return result.scalar_one_or_none()

#更新用户信息
async def update_user(db:AsyncSession,username:str,user_data:UserUpdateRequest):
    query=update(User).where(User.username==username).values(**user_data.model_dump(exclude_unset=True,
                                                                                    exclude_none=True))
    result=await db.execute(query)
    await db.commit()
    #检查更新
    if result.rowcount==0:
        raise HTTPException(status_code=404,detail="用户不存在")
    #获取更新后的用户
    updated_user=await get_users_by_username(db,username)
    return updated_user

#修改用户密码
async def change_password(db:AsyncSession,user:User,old_password:str,new_password:str):
    #验证旧密码
    if not security.verify_password(old_password,user.password):
        return False
    #新密码加密
    hashed_new_pwd=security.get_hash_password(new_password)
    user.password=hashed_new_pwd
    #更新：由SQLAlchemy真正接管这个User对象，确保可以commit
    #规避session过期或者关闭导致的不能提交的问题
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True
