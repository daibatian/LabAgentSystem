from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class User(Base):
    __tablename__ = "users"  # 后续会创建users表
    __table_args__ = {"comment": "用户信息表"}  # 表注释

    username: Mapped[str] = mapped_column(
        String(50), comment="账号", unique=True, sort_order=1
    )
    password: Mapped[str] = mapped_column(String(255), comment="密码", sort_order=2)
    role: Mapped[str] = mapped_column(String(50), comment="角色", sort_order=3)
    name: Mapped[str] = mapped_column(String(50), comment="名称", sort_order=4)
    email: Mapped[str | None] = mapped_column(
        String(50), comment="邮箱", nullable=True, sort_order=5
    )
    phone: Mapped[str | None] = mapped_column(
        String(50), comment="手机号", nullable=True, sort_order=6
    )
    avatar: Mapped[str | None] = mapped_column(
        String(50), comment="头像", nullable=True, sort_order=7
    )
    status: Mapped[int] = mapped_column(
        default=1, comment="状态：0-正常 1-禁用", sort_order=8
    )
