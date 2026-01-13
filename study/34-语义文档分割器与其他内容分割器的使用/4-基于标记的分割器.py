#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/12 20:51
@Author  : LCH
@File   : 4-基于标记的分割器.py
"""
import tiktoken
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def calculate_token_count(query: str) -> int:
    """计算传入文本的token数"""
    encoding = tiktoken.encoding_for_model("text-embedding-3-large")
    return len(encoding.encode(query))


separators = [
    r"\n\n",
    r"\n",
    r"。|！|？",
    r"\.\s|\!\s|\?\s",
    r"；|;\s",
    r"，|,\s",
    r" ",
    r""
]

# 1.定义加载器和文本分割器
loader = UnstructuredFileLoader("./科幻短篇.txt")
text_splitter = RecursiveCharacterTextSplitter(
    separators=separators,
    is_separator_regex=True,
    chunk_size=500,
    chunk_overlap=50,
    length_function=calculate_token_count,
)
#
# text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#     model_name="text-embedding-3-large",
#     chunk_size=500,
#     chunk_overlap=50,
#     separators=separators,
#     is_separator_regex=True,
# )

# 2.加载文档并执行分割
documents = loader.load()
chunks = text_splitter.split_documents(documents)

# 3.循环打印分块内容
for chunk in chunks:
    print(f"块大小: {len(chunk.page_content)}, 元数据: {chunk.metadata}")
