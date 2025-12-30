#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2025/12/30 20:44
@Author  : LCH
@File   : 2-configurable_field替换提示词.py
"""
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import ConfigurableField

# 1.创建提示词模板并配置支持动态配置字段
prompt = PromptTemplate.from_template("请写一个关于{subject}的笑话").configurable_fields(
    template=ConfigurableField(
        id="prompt_template",
    )
)

# 2.传递配置更改prompt_template
content = prompt.invoke({"subject": "小猫"},
                        config={"configurable": {"prompt_template": "请写一个关于{subject}的 Fact-checking 笑话"}})
print(content)
