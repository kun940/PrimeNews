import inspect
import json
from typing import Any

import redis.asyncio as redis
REDIS_HOST="localhost"
REDIS_PORT=6379
REDIS_DB=0

#创建Redis的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True #将字节流解码为字符串
)

#设置 和 读取（字符串 和 列表或字典）
#读取：字符串
async def get_cache(key:str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None

#读取：列表或字典
async def get_json_cache(key:str):
    try:
     data= await redis_client.get(key)
     if data:
         return json.loads(data) #反序列化
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None

#设置缓存 setex
async def set_cache(key:str,value:Any,expire:int=60):
    try:
        if isinstance(value,(dict,list)):
            #序列化
            value = json.dumps(value,ensure_ascii=False)
        await redis_client.set(key,value,ex=expire)
        return True
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return False