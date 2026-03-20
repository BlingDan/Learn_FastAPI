from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, String, Float, func, select
from datetime import datetime

app = FastAPI()

# 1.创建异步引擎
ASYNC_DATABASE_URL = "mysql+aiomysql://root:tc2a_FLW@127.0.0.1:3306/fastapi_first"
async_engin = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 输出sql日志
    pool_size=10,   # 设置连接池活跃的连接数
    max_overflow=20, # 允许额外的连接数
    )

# 2. 定义模型类： 基类 + 表对应的模型类

# 基类： 创建时间，更新时间； 书籍表：id,书名，作者，出版社
class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), default=func.now,comment="更新时间")
    update_time: Mapped[datetime] = mapped_column(DateTime, insert_default=func.now(), default=func.now, onupdate=func.now(),comment="更新时间")

class Book(Base):
    __tablename__ = "book" # 映射到数据库中的 book 表
    id: Mapped[int] = mapped_column(primary_key=True, comment="书籍ID")
    bookname: Mapped[str] = mapped_column(String(255), comment="书名")
    author: Mapped[str] = mapped_column(String(255), comment="作者")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")
    
# 3.建表：定义函数建表 -> 在 fastapi 启动时候调用建表函数
async def  create_tables():
    # 获取数据库的异步引擎, 创建事务 - 建表
    async with async_engin.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # 使用base模型类的元数据创建表

@app.on_event("startup")
async def startup_event():
    await create_tables()

@app.get("/")
async def root():
    return {"message": "hello world"}



# 需求： 查询功能的接口，查询图书 -> 1. 依赖注入：创建依赖项获取数据库会话 +  2.Depends 注入路由处理函数

# 这个async_sessionmaker() 是一个工厂函数，他会创建一个session类并且返回。
# 在 fastapi 中经常，通常会配合这个工厂对象，在依赖注入depends里面每次为新的HTTP请求生成一个独立的数据库会话，处理完之后再关闭
AsyncSessionLocal = async_sessionmaker(
    bind=async_engin, # 绑定数据库引擎
    class_ =AsyncSession, # 指定会话类 ？？？
    expire_on_commit=False #提交会话后不会过期
)

# 创建依赖项：每次请求都会调用这个对象，返回一个session
async def get_database_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session # yield 主要用来暂停当前函数，并把后面带的东西返回给调用者
            await session.commit() # 提交事务 。 这个关键词大部分情况下都是在异步函数中async使用。在异步函数里面等待异步任务
        except Exception as e:
            await session.rollback() # 异常，回滚函数
            raise # 抛出异常
        finally:
            await session.close() # 关闭会话

@app.get("/book/book_list")
async def get_books_list(db:AsyncSession=Depends(get_database_session)):
    # 1. 创建查询对象
    stmt = select(Book)
    # 2. 执行查询
    result = await db.execute(stmt)
    # 3. 获取结果
    books = result.scalars().all()
    return books