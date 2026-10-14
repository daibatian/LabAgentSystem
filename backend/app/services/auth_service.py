import email

from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.utils.password import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.common.exceptions import BusinessException


def login(db: Session, data: LoginRequest):
    # 在这里实现登录逻辑，例如验证用户名和密码
    user = db.query(User).filter(User.username == data.username).first()

    # 判断账号和密码是否正确
    if not user or not verify_password(data.password, user.password):
        raise BusinessException(message="用户名或密码错误", code=401)
    # 判断账号是否被禁用
    if user.status != 1:
        raise BusinessException(message="账号已被禁用，请联系管理员", code=403)

    # 生成JWT token
    token = create_access_token(user.id)

    return LoginResponse(token=token, user=UserResponse.model_validate(user))


def register(db: Session, data: RegisterRequest) -> None:
    exists = db.query(User).filter(User.username == data.username).first()
    if exists:
        raise BusinessException(message="账号已存在", code=400)

    user = User(
        username=data.username,
        password=hash_password(data.password),
        name=data.name or data.username,
        role="student",
        status=1,
        email="",
        phone="",
        avatar="",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
