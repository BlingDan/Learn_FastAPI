from enum import Enum
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse,FileResponse

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

"""
response_class： 响应类型 比如html, json
response_model: 响应模型，规定了返回的数据类型，并对返回的数据进行校验
"""
# 响应类型 HTML 格式
@app.get("/html", response_class=HTMLResponse)
async def get_html():
    return HTMLResponse("<h1>Hello World</h1>")

# 响应类型 文件格式
@app.get("/file", response_class=FileResponse)
async def get_file():
    path = "./files/Cat.jpg"
    return FileResponse(path)

# 自定义类型响应数据格式
class News(BaseModel):
    id: int
    title: str
    content: str
@app.get("/news/{id}", response_model=News)
async def get_news(id: int):
    id_list = [i for i in range(1, 11)]
    if id not in id_list:
        raise HTTPException(status_code=404, detail="news not found")
        
    # 这里不加News也是可以，在参数中已经注明了model = News，
    # FastAPI会 1.按照News这个模型去校验返回值 2.把结果序列化成json响应
    return News(
        id = id,
        title = f'this is news {id}',
        content = "this is a good and popular news"
    )

# 请求体参数 1.定义类型 2.类型注解
# 在请求中 post 侧重于创建 put 侧重于更新
## eg 用户的注册信息 需要账号密码 -> str
# class User(BaseModel):
#     username: str = Field(..., min_lenght = 2, max_length = 10)
#     password: str = Field(..., min_length = 6, max_length = 16, description="input number and letter")

# @app.post("/register")
# async def register(user:User):
#     return {"username": user.username, "password": user.password}




@app.get("/")
async def hello():
    return {"message": "Hello World"}

# @app.get("/book/{book_id}")
# async def get_book(book_id: int = Path(..., gt=0, lt=1000)):
#     return {"id": book_id, "title": f"this is book {book_id}"}

# 查询参数和Query类型
# @app.get("/books/list")
# async def get_book_list(
#     category: str = Query(default="python development", min_length=5, max_length=255),
#     price: float = Query(..., 
#     lt=100, gt=50)
#     ):
#     return {"category": category, "price": price}


