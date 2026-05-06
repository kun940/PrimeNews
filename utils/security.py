from passlib.context import CryptContext
#创建密码上下文
pwq_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#密码加密
def get_hash_password(password:str):
    return pwq_context.hash(password)

#密码校验
def verify_password(plain_password:str,hashed_password:str):
    return pwq_context.verify(plain_password, hashed_password)