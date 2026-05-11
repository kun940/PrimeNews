#新闻模块的增删改查操作(旁路缓存策略版)
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_caache import get_cached_categories, set_cache_categories, get_cache_news_list, set_cache_news_list
from models.news_models import Categories, News
from sqlalchemy import select, func, update

from schemas.newsbase import NewsItemBase


#获取新闻种类
async def get_categories(db:AsyncSession,skip:int=0, limit:int=10):
    #先尝试从缓存中获取数据
    cached_categories=await get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt=select(Categories).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories=result.scalars().all()#orm对象

    #写入缓存
    if categories:
        categories=jsonable_encoder(categories)
        await set_cache_categories(categories)
    #返回数据
    return categories
#获取新闻列表
async def get_news_list(db:AsyncSession,category_id:int,skip:int=0, limit:int=10):
    #先查缓存
    page=skip // limit+1
    cached_list=await get_cache_news_list(category_id,page,limit)#缓存数据是json
    if cached_list:
        return [News(**item)for item in cached_list]
    #查询的是指定分类下所有新闻
    stmt=select(News).where(News.category_id==category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list= result.scalars().all()
    #写入缓存
    if news_list:
        #先把orm数据转换成字典才能写入缓存
        #orm转成pydantic，再转为字典
        #by_alias=False 不使用别名，保存python风格
        news_data=[NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in news_list]
        await set_cache_news_list(category_id,page,limit,news_data)
    return news_list
#获取新闻总量
async def get_news_count(db:AsyncSession,category_id:int):
    stmt=select(func.count(News.id)).where(News.category_id==category_id)
    result = await db.execute(stmt)
    return result.scalar()

#获取新闻详情
async def get_news_details(db:AsyncSession,news_id:int):
    stmt=select(News).where(News.id==news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
#更新浏览量
async def increase_news_views(db:AsyncSession,news_id:int):
    stmt=update(News).where(News.id==news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    #更新操作需要检查数据库是否命中数据
    return result.rowcount>0
#获取推荐相关新闻列表
async def get_related_news(db:AsyncSession,category_id:int,news_id:int,limit:int=5):
    #按照浏览量和发布时间排序
    stmt=(select(News).
          where(News.category_id==category_id,News.id!=news_id).
          order_by(News.views.desc(),News.publish_time.desc()).
          limit(limit)
          )
    result = await db.execute(stmt)
    related_news=result.scalars().all()
    #只提取核心数据
    return[{
    "id": news_details.id,
    "title": news_details.title,
    "content": news_details.content,
    "image": news_details.image,
    "author": news_details.author,
    "publishTime": news_details.publish_time,
    "categoryId": news_details.category_id,
    "views": news_details.views
    }for news_details in related_news]


