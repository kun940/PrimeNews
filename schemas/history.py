from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict

from schemas.newsbase import NewsItemBase


class HistoryAddRequest(BaseModel):
    news_id:int=Field(...,alias="newsId")

#浏览历史新闻详情
class HistoryNewsItemResponse(NewsItemBase):
    view_time:datetime =Field(...,alias="viewTime")
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
#浏览历史列表接口响应模型类
class HistoryListResponse(BaseModel):
    list: List[HistoryNewsItemResponse]
    total: int
    has_more: bool
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )