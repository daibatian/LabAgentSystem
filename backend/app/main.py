from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.models.user import User
from app.models.lab import Lab
from app.models.equipment import Equipment
from app.models.reservation import Reservation
from app.database import engine, Base
from app.api import api
from fastapi.middleware.cors import CORSMiddleware
from app.common.exceptions import (
    BusinessException,
    business_exception_handler,
    http_exception_handler,
    validation_excpetion_hadler,
    global_excpetion_hadler,
)
from app.config import UPLOAD_DIR
import asyncio
import logging
from app.services import reservation_service
from contextlib import asynccontextmanager
from app.services import kb_service

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)  # 创建数据库表结构


# 创建定时任务
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 预热向量库：模型加载（约 15s）挪到启动阶段，避免首个请求超过前端 30s 超时
    try:
        await asyncio.to_thread(
            kb_service.warmup
        )  # to_thread：别阻塞事件循环，使用asyncio放到其他线程池，不和主线程一起
    except Exception:
        logger.exception("向量库预热失败，服务继续启动")
    # 启动项目开启异步的扫描任务
    task = asyncio.create_task(reservation_service.run_expire_scan())
    try:
        yield
    finally:
        task.cancel()  # 关闭项目同时取消异步任务
        await asyncio.gather(
            task, return_exceptions=True
        )  # 取消任务，不再把错误信息抛给lifespan


app = FastAPI(lifespan=lifespan)

# 将 API 路由注册到FastAPI应用中
app.include_router(api)

# 注册异常处理器
app.add_exception_handler(BusinessException, business_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_excpetion_hadler)
app.add_exception_handler(Exception, global_excpetion_hadler)

# 挂在静态的文件目录，把服务器上某个本地目录暴露成一个可通过 URL 访问的静态资源目录。
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 前端默认端口
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法，包括 OPTIONS
    allow_headers=["*"],  # 允许所有请求头
)


@app.get("/")
def root():
    return {"message": "Hello FastAPI"}
