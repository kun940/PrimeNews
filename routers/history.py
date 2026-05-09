from fastapi import APIRouter
from fastapi.params import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.database_config import get_db
from crud.history import add_news_history, get_news_history_list, delete_news_history, clear_news_history
from models import history
from models.users_models import User
from schemas.history import HistoryAddRequest, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(
    prefix="/api/history",
    tags=["history"]
)

@router.post("/add")
async def add_history(
        data: HistoryAddRequest,
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    history=await add_news_history(db, user.id, data.news_id)
    return success_response(message="新增浏览历史成功",data=history)

@router.get("/list")
async def get_history_list(
        page: int = Query(1,ge=1),
        page_size: int = Query(10,ge=1,le=100,alias="pageSize"),
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    rows,total=await get_news_history_list(db, user.id,page, page_size)
    has_more = total > page * page_size
    history_list = [{
        **news.__dict__,
        "view_time":view_time,
    } for news, view_time in rows]
    #格式化响应内容
    data = HistoryListResponse(list=history_list, total=total, has_more=has_more)
    return success_response(message="获取浏览历史列表成功",data=data)

@router.delete("/delete/{history_id}")
async def delete_history(
        history_id: int,
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    await delete_news_history(db, history_id)
    return success_response(message="删除浏览历史成功")

@router.delete("/clear")
async def clear_history(
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    await clear_news_history(db, user.id)
    return success_response(message="清空成功")
