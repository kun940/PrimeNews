from sqlite3 import IntegrityError
from sqlalchemy.exc import SQLAlchemyError

from fastapi import HTTPException
from utils.exception import http_exception_handler, sqlalchemy_error_handler, general_exception_handler

from utils.exception import integrity_error_handler


def register_exception_handlers(app):
    """
    注册全局异常处理
    """
    app.add_exception_handler(HTTPException,http_exception_handler)#业务层
    app.add_exception_handler(IntegrityError,integrity_error_handler)#数据完整性约束
    app.add_exception_handler(SQLAlchemyError,sqlalchemy_error_handler)#数据库
    app.add_exception_handler(Exception,general_exception_handler)#默认兜底