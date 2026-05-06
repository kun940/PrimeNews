from http.client import HTTPException

from fastapi import APIRouter,Depends,Query

from config.database_config import get_db
from crud import news
from config.database_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from crud.news import increase_news_views

#创建APIRouter实例
#prefix（路由前缀） tags（分组标签）
router = APIRouter(prefix="/api/news", tags=["news"])

#获取新闻种类
@router.get("/categories")
async def get_categories(skip:int=0, limit:int=10,db:AsyncSession=Depends(get_db)):
    #先获取数据库里面新闻分类数据
    categories= await news.get_categories(db,skip,limit)
    return {
        "code":200,
        "message":"获取新闻分类成功",
        "data":categories
    }
#获取新闻列表
@router.get("/list")
async def get_news_list(
    category_id:int=Query(...,alias="categoryId"),
    page:int=0,
    page_size:int=Query(10,alias="pageSize",le=100),
    db:AsyncSession=Depends(get_db)
):
    news_list=await news.get_news_list(db,category_id,(page-1)*page_size,page_size)
    total=await news.get_news_count(db,category_id)
    hasmore=((page-1)*page_size+len(news_list))<total
    return {
        "code":200,
        "message":"获取新闻列表成功",
        "data":{
            "list":news_list,
            "total":total,
            "hasMore":hasmore
        }
    }
#获取新闻详情
@router.get("/detail")
async def get_news_detail(
    news_id:int=Query(...,alias="id"),db:AsyncSession=Depends(get_db)
):
    #获取新闻详情+浏览量加一+相关新闻
    news_details=await news.get_news_details(db,news_id)
    if not news_details:
        raise HTTPException(status_code=404,detail="新闻不存在")

    views_res=await increase_news_views(db,news_id)
    #检查是否命中数据库
    if not views_res:
        raise HTTPException(status_code=404,detail="新闻不存在")

    related_results=await news.get_related_news(db,news_details.category_id,news_id)
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_details.id,
            "title": news_details.title,
            "content": news_details.content,
            "image": news_details.image,
            "author": news_details.author,
            "publishTime": news_details.publish_time,
            "categoryId": news_details.category_id,
            "views": news_details.views,
            "relatedNews":related_results
        }
    }