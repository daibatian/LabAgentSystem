from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.common.exceptions import BusinessException
from app.database import get_db
from app.utils.jwt import decode_access_token
from app.models.user import User

"""
FastAPI 会自动生成 OpenAPI（Swagger）文档。
当你在 Swagger UI（/docs）页面时，右上角会有一个 "Authorize" 按钮。
点击后弹出的登录框，就是根据这个 tokenUrl 生成的。
即使你把它写错，代码运行也不会报错，只是 Swagger UI 的 Authorize 功能会失效。
后面的 get_current_user 函数中，Depends(oauth2_scheme) 会自动从请求头中获取 Authorization 字段的值，并进行验证，和这里的 tokenUrl 没有直接关系。
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", scheme_name="JWT")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户
    """
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录")
    # 获取用户ID
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="无效的登录凭证")
    # 查询用户信息
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系管理员")
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """判断JWT Token内角色是否为admin"""
    if current_user.role != "admin":
        raise BusinessException(message="无权限访问", code=401)
    return current_user
