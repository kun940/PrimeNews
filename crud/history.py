from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from models.history import History
from models.news_models import News


#新增浏览记录
async def add_news_history(
        db: AsyncSession,
        user_id: int,
        news_id:int
):
    #检查是否浏览过新闻
    query=select(History).where(History.user_id==user_id,History.news_id==news_id)
    result=await db.execute(query)
    history = result.scalar_one_or_none()
    if history is None:
        history=History(user_id=user_id,news_id=news_id,view_time=datetime.now())
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history
    else:
        history.view_time=datetime.now()
        await db.commit()
        await db.refresh(history)
        return history

#获取浏览新闻列表
async def get_news_history_list(
        db: AsyncSession,
        user_id: int,
        page: int=1,
        page_size: int=10
):
    #先查询该用户的浏览历史总量
    count_query=select(func.count(History.id)).where(History.user_id==user_id)
    count_result=await db.execute(count_query)
    total=count_result.scalar_one_or_none()
    #联表查询浏览历史中的新闻详情
    offset=(page-1)*page_size
    query=(select(News,History.view_time.label("viewTime"))
           .join(History,History.news_id == News.id)
            .where(History.user_id==user_id)
            .order_by(History.view_time.desc())
           .offset(offset).limit(page_size))
    result = await db.execute(query)
    rows = result.all()
    return rows,total

#删除单条浏览记录
async def delete_news_history(
        db: AsyncSession,
        history_id: int
):
    query=delete(History).where(History.news_id==history_id)
    result=await db.execute(query)
    await db.commit()
    return result.rowcount>0

#清空浏览记录
async def clear_news_history(
        db: AsyncSession,
        user_id: int
):
    query=delete(History).where(History.user_id==user_id)
    result=await db.execute(query)
    await db.commit()
    



