#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/28 11:31
@Author  : LCH
@File   : builtin_provider_manager.py
"""
import os

import yaml
from injector import inject, singleton
from pydantic import BaseModel, Field

from internal.core.tools.builtin_tools.entites.provider_entity import ProviderEntity, Provider


@inject
@singleton
class BuiltinProviderManager(BaseModel):
    """内置服务提供商总管家"""
    provider_map: dict[str, Provider] = Field(default_factory=dict)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_providers()

    def get_provider(self, provider_name: str) -> Provider:
        """从内存中拿指定的厂商"""
        return self.provider_map.get(provider_name)

    def get_providers(self) -> list[Provider]:
        """获取所有厂商列表"""
        return list(self.provider_map.values())

    def _init_providers(self):
        """系统启动时，把所有的厂商对象全部实例化！"""
        if self.provider_map: return
        provider_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(provider_path, "providers.yaml"), encoding="utf-8") as f:
            providers = yaml.safe_load(f)
        # 遍历 providers.yaml 里的每一项
        for position, provider in enumerate(providers):
            # 将基础数据转为 ProviderEntity（第一步造的零件）
            provider_entity = ProviderEntity(**provider)

            # 【奇迹时刻】：实例化 Provider！
            # 这一步会自动触发我们之前写的 _provider_init，
            # 它会自动去扫描名下所有的工具、并且利用 dynamic_import 挂载真实函数。
            self.provider_map[provider_entity.name] = Provider(
                name=provider_entity.name,
                position=position + 1,
                provider_entity=provider_entity,
            )
