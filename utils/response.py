#通用成功响应
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
def success_response(message:str="success",data=None):
    content={
        "code":200,
        "message":message,
        "data":data
    }
    #任何FastAPI、Pydantic、ORM对象都以同样的json模板响应
    return JSONResponse(content=jsonable_encoder(content))