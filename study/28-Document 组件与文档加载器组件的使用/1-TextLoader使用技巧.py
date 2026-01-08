#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/8 19:20
@Author  : LCH
@File   : 1-TextLoader使用技巧.py
"""
from langchain_community.document_loaders import TextLoader

loader = TextLoader("./电商产品数据.txt", encoding="utf-8")

documents = loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
