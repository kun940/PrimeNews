from fastapi import FastAPI

from utils.exception_handlers import register_exception_handlers
from routers import news,users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
#注册全局异常处理器
register_exception_handlers(app)

#跨域资源共享中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",  # 前端地址
    "http://127.0.0.1:5173"],#允许的源，开发阶段允许所有源，生产环境需要指定源
    allow_credentials=True,#允许携带cookie
    allow_methods=["*"],#允许的请求方法
    allow_headers=["*"],#允许的请求头
)
#挂载路由/注册路由
app.include_router(news.router)
app.include_router(users.router)