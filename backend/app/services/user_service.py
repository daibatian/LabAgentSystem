from app.api import user
from app.common.response import PageResponse
from app.models.user import User
from app.schemas.user import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
    PasswordUpdateRequest,
)
from sqlalchemy.orm import Session
from app.utils.password import hash_password, verify_password
from app.common.exceptions import BusinessException
from operator import or_


def get_user_info(user: User) -> UserResponse:
    return UserResponse.model_validate(user)


def update_user_info(db: Session, user: User, data: UserUpdateRequest):
    user_dict = data.model_dump(
        exclude_none=True,
        exclude={"role", "status", "password"},  # 防止用户能够修改角色、状态
    )  # pydatic对象转换成字典
    for field, value in user_dict.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def update_password(db: Session, user: User, data: PasswordUpdateRequest):
    if not verify_password(data.old_password, user.password):
        raise BusinessException(message="原密码错误", code=400)
    if data.old_password == data.new_password:
        raise BusinessException(message="新密码不能与原密码相同", code=400)
    user.password = hash_password(data.new_password)
    db.commit()


def get_user_page_list(
    db: Session, page: int, page_size: int, keywords: str | None = None
):
    # select * from user where username like '%张%' or name like '%张%';
    query = db.query(User)
    if keywords:
        query = query.filter(
            or_(
                User.username.ilike(f"%{keywords}%"), User.name.ilike(f"%{keywords}%")
            )  # ilike是不区分大小写
        )
    total = query.count()
    offset_index = (page - 1) * page_size
    items = (
        query.order_by(User.id.desc()).offset(offset_index).limit(page_size).all()
    )  # 分页查询并且根据id倒序排序
    return PageResponse(
        list=[
            UserResponse.model_validate(item) for item in items
        ],  # items元组返回的是User对象，这里处理成返回的是自定义的UserResponse对象
        total=total,
    )


def create_user(db: Session, data: UserCreateRequest):
    """新增用户"""
    exist = db.query(User).filter(User.username == data.username).first()
    if exist:
        raise BusinessException(message="账号已存在", code=400)
    user = User(
        username=data.username,
        password=hash_password(data.password),
        name=data.name,
        role=data.role,
        email=data.email,
        phone=data.phone,
        avatar=data.avatar,
        status=data.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def update_user(db: Session, user_id: int, data: UserUpdateRequest):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BusinessException(message="用户不存在", code=400)
    payload = data.model_dump(exclude_none=True)
    for filed, value in payload.items():
        setattr(user, filed, value)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def delete_user(db: Session, user_id: int, current_user: User):
    """删除用户"""
    if user_id == current_user.id:
        raise BusinessException(
            message="不能删除当前登录的账号", code=400
        )  # 防止把自己删除了
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise BusinessException(message="用户不存在", code=400)
    db.delete(user)
    db.commit()
