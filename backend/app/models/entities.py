"""Minimal skeleton tables; not the frozen production data contract."""
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class Product(Base):
    __tablename__ = 'products'
    __table_args__ = (UniqueConstraint('tenant_id', 'platform', 'platform_product_id'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, index=True, default=1)
    platform: Mapped[str] = mapped_column(String(32))
    platform_product_id: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(512))
    category: Mapped[str] = mapped_column(String(128), default='')
    status: Mapped[str] = mapped_column(String(32), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ReviewTask(Base):
    __tablename__ = 'review_tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, index=True, default=1)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), index=True)
    stage: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default='PENDING')
    comment: Mapped[str] = mapped_column(Text, default='')


class ContentJob(Base):
    __tablename__ = 'content_jobs'
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, index=True, default=1)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), index=True)
    status: Mapped[str] = mapped_column(String(32), default='PENDING')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(Integer, index=True, default=1)
    action: Mapped[str] = mapped_column(String(64))
    target: Mapped[str] = mapped_column(String(128))
    detail: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
