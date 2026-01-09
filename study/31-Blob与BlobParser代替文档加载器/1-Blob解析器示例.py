#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/8 20:14
@Author  : LCH
@File   : 1-Blob解析器示例.py
"""
from typing import Iterator

from langchain_core.document_loaders import BaseBlobParser
from langchain_core.documents import Document
from langchain_core.documents.base import Blob


class CustomParser(BaseBlobParser):
    """自定义解析器，用于将传入的文本二进制数据的每一行解析成Document"""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        line_number = 0
        with blob.as_bytes_io() as f:
            for line in f:
                yield Document(
                    page_content=line,
                    metadata={
                        "source": blob.source,
                        "line_number": line_number,
                    }
                )
                line_number += 1


# 1.加载blob数据
blob = Blob.from_path("./喵喵.txt")
parser = CustomParser()

# 2.解析得到文档数据
documents = list(parser.lazy_parse(blob))

print(documents)
print(len(documents))
print(documents[0].metadata)
