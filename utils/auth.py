#整合token查询功能

from fastapi import Header,Depends,status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.database_config import get_db
from crud import users

async def get_current_user(
        authorization: str=Header(...,alias="Authorization"),
        db:AsyncSession=Depends(get_db)
):
    token=authorization.replace("Bearer ","")
    user=await users.get_user_by_token(db,token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="无效的令牌或已过期的令牌")
    return user