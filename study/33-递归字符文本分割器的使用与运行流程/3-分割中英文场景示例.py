#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/11 18:38
@Author  : LCH
@File   : 3-分割中英文场景示例.py
"""
from langchain_community.document_loaders import UnstructuredMarkdownLoader

# 1.创建加载器和文本分割器
loader = UnstructuredMarkdownLoader("./项目API文档.md")

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1.创建加载器和文本分割器
loader = UnstructuredMarkdownLoader("./项目API文档.md")
# separators = [
#     "\n\n",  # ① 段落
#     "\n",  # ② 换行
#     "。|！|？",  # ③ 中文句号
#     "\.\s|\!\s|\?\s",  # ④ 英文句号
#     "；|;\s",  # ⑤ 分号
#     "，|,\s",  # ⑥ 逗号
#     " ",  # ⑦ 空格
#     ""  # ⑧ 单字符兜底
# ]
separators = [
    r"\n\n",
    r"\n",
    r"。|！|？|……|！？",
    r"\.\s|\!\s|\?\s",
    r"；|;\s",
    r"，|,\s",
    r" ",
    r""
]
text_splitter = RecursiveCharacterTextSplitter(
    separators=separators,
    is_separator_regex=True,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)

# 2.加载文档与分割
documents = loader.load()
chunks = text_splitter.split_documents(documents)

for chunk in chunks:
    print(f"块大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")

print(chunks[2].page_content)
itter = RecursiveCharacterTextSplitter(
    separators=separators,
    is_separator_regex=True,
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
)

# 2.加载文档与分割
documents = loader.load()
chunks = text_splitter.split_documents(documents)

for chunk in chunks:
    print(f"块大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")

print(chunks[2].page_content)
