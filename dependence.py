from fastapi import FastAPI, Query, Depends  # 1.导入Depends

app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "Hello World"}


# 为什么要使用依赖项来复用代码逻辑，而不是直接使用中间件，因为中间件是全局的，无法实现具体代码逻辑的复用


# 2.定义依赖项
# 分页参数逻辑共用：新闻列表和用户列表
async def common_parameters(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, description="each page's item")
):
    return {"skip": skip, "limit": limit}


@app.get("/news/new_list")
async def get_news_list(common = Depends(common_parameters)): # 注入依赖
    return common

@app.get("/usr/usr_list")
async def get_usr_list():
    return {"message": "usr_list"}