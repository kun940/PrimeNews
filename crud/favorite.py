from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select, delete, func, desc
from sqlalchemy.orm import join

from models.favorite_models import Favorite
from models.news_models import News


#检查收藏状态
async def is_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
)->bool:
    query=select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result=await db.execute(query)
    #是否有收藏记录
    return result.scalar_one_or_none() is not None

#添加收藏
async def add_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    post=Favorite(
        user_id=user_id,
        news_id=news_id
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post

#取消收藏
async def remove_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt=delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result=await db.execute(stmt)
    await db.commit()
    return result.rowcount>0

#获取收藏列表
async def get_news_favorite(
        db: AsyncSession,
        user_id: int,
        page: int=1,
        page_size: int=10
):
    #查询收藏新闻总量
    count_query=select(func.count(Favorite.news_id)).where(Favorite.user_id == user_id)
    count_result=await db.execute(count_query)
    total=count_result.scalar_one
    #查询收藏新闻+收藏时间排序+分页
    offset=(page-1)*page_size
    query=(select(News,Favorite.created_at.label("favorite_time"),Favorite.id.label("favorite_id"))
    .join(Favorite,Favorite.news_id == News.id)
    .where(Favorite.user_id == user_id)
    .order_by(desc("favorite_time"))
    .offset(offset).limit(page_size)
           )
    result=await db.execute(query)
    rows=result.all()
    return rows,total

#清空收藏
async def remove_all_favorite(
        db: AsyncSession,
        user_id: int
):
    stmt=delete(Favorite).where(Favorite.user_id == user_id)
    result=await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0