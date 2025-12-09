#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/9 19:51
@Author  : LCH
@File   : app_service.py
"""
import uuid
from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy
from injector import inject

from internal.extension.database_extension import db
from internal.model.app import App


@inject
@dataclass
class AppService:
    """应用服务"""
    db: SQLAlchemy

    def create_app(self) -> App:
        # 1.创建模型实体类
        app = App(name="测试机器人", account_id=uuid.uuid4(), icon="", description="")
        # 2.将实体类添加到session会话中
        db.session.add(app)
        # 3,提交session会话
        db.session.commit()
        return app

    def get_app(self, id: uuid.UUID) -> App:
        return db.session.query(App).get(id)

    def update_app(self, id: uuid.UUID) -> App:
        app = self.get_app(id)
        app.name = "测试修改"
        self.db.session.commit()
        return app

    def delete_app(self, id: uuid.UUID) -> App:
        app = self.get_app(id)
        self.db.session.delete(app)
        self.db.session.commit()
        return app
