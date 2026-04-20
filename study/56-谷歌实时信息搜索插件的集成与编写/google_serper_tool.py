#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/4/8 21:17
@Author  : LCH
@File   : google_serper_tool.py
"""
import dotenv
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
from pydantic.v1 import BaseModel, Field


class GoogleSerperArsScheme(BaseModel):
    query: str = Field(description="谷歌搜索")


dotenv.load_dotenv()
google_serper = GoogleSerperRun(
    name="google-serper",
    description="搜索器",
    args_scheme=GoogleSerperArsScheme,
    api_wrapper=GoogleSerperAPIWrapper()
)

print(google_serper.invoke("周杰伦太阳之子"))
