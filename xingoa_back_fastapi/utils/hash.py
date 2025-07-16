from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希值是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码的bcrypt哈希值"""
    return pwd_context.hash(password)

# 生成的hash = $2b$12$eo.4NXuiesWg4kq8iWhodeqKSbfsnWK3qVTefUJYfOD/6jTnljwFi
# 长度 : 60

if __name__ == "__main__":
    pwd = "dasdasd"
    pwd_hashed = get_password_hash(pwd)
    print(f"生成的hash = {pwd_hashed}")
    print(f"长度 : {len(pwd_hashed)}")