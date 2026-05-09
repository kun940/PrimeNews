from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict

from schemas.newsbase import NewsItemBase


class FavoriteCheckResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    is_favorite: bool=Field(...,alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    news_id: int=Field(...,alias="newsId")

#收藏的新闻详情
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(...,alias="favoriteId")
    favorite_time:datetime = Field(...,alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )

#收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    list: List[FavoriteNewsItemResponse]
    total: int
    has_more: bool
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
