#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/9 19:17
@Author  : LCH
@File   : app.py
"""

from sqlalchemy import (
    Column,
    UUID,
    String,
    DateTime,
    Text,
    PrimaryKeyConstraint,
    Index,
    text,
)

from internal.extension.database_extension import db


class App(db.Model):
    """应用模型"""
    __tablename__ = "app"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pk_app_id"),
        Index("idx_app_account_id", "account_id"),
    )

    id = Column(UUID, nullable=False, server_default=text("uuid_generate_v4()"))
    account_id = Column(UUID)
    name = Column(String(255), nullable=False, server_default="'':character varying")
    icon = Column(String(255), nullable=False, server_default="'':character varying")
    description = Column(Text, nullable=False, server_default="'':text")
    status = Column(String(255), nullable=False, server_default="'':character varying")
    updated_at = Column(DateTime, nullable=False,
                        server_default="CURRENT_TIMESTAMP(0)",
                        server_onupdate="CURRENT_TIMESTAMP(0)")
    created_at = Column(DateTime, nullable=False, server_default="CURRENT_TIMESTAMP(0)")
