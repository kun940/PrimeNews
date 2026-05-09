from datetime import datetime
from sqlalchemy import UniqueConstraint, Index, Integer,ForeignKey,DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped,mapped_column
from models.news_models import News
from models.users_models import User
class Base(DeclarativeBase):
    pass
class Favorite(Base):
    """
    收藏表0RM模型
    """
    __tablename__='favorite'
    #创建索引
    _table_args_ = (
        UniqueConstraint('user_id', 'news_id', name='user_niews_unique'),
        Index('fk_favorite_user_idx','user_id'),
        Index('fk_favorite_news_idx', 'news_id')
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True,comment="收藏ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False,comment="用户ID")
    news_id: Mapped[int] = mapped_column(Integer, ForeignKey(News.id), nullable=False,comment="新闻ID")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow,nullable=False,comment="收藏时间")

    def _repr_(self):
        return f"<Favorite(id={self.id}, user_id={self.user_id},news_id={self.news_id}, created_at={self.created_at})>"


