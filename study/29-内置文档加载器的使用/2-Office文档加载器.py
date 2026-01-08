#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/8 19:28
@Author  : LCH
@File   : 2-Office文档加载器.py
"""
from langchain_community.document_loaders import UnstructuredExcelLoader, UnstructuredWordDocumentLoader, \
    UnstructuredPowerPointLoader

xlxs_loader = UnstructuredExcelLoader("./员工考勤表.xlsx")
documents = xlxs_loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)

print("===================>")

word_loader = UnstructuredWordDocumentLoader("./喵喵.docx")
documents = word_loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)

print("===================>")

ppt_loader = UnstructuredPowerPointLoader("./章节介绍.pptx")
documents = ppt_loader.load()

print(documents)
print(len(documents))
print(documents[0].metadata)
