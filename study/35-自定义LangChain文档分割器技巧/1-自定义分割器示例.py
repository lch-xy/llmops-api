#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/13 10:24
@Author  : LCH
@File   : 1-自定义分割器示例.py
"""
from typing import List

import jieba.analyse
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import TextSplitter


class CustomTextSplitter(TextSplitter):
    """自定义文本分割器"""

    def __init__(self, separator: str, top_k: int = 10, **kwargs) -> None:
        super().__init__(**kwargs)
        self._separator = separator
        self._top_k = top_k

    def split_text(self, text: str) -> List[str]:
        """分割传入的文本为字符串列表"""
        split_texts = text.split(self._separator)
        text_keywords = []
        for split_text in split_texts:
            text_keywords.append(
                jieba.analyse.extract_tags(split_text, topK=self._top_k, withWeight=True)
            )

        # return [",".join(keywords) for keywords in text_keywords]
        return [
            ",".join(f"{w}:{s:.3f}" for w, s in keywords)
            for keywords in text_keywords
        ]


# 1.创建加载器与分割器
loader = UnstructuredFileLoader("./科幻短篇.txt")
text_splitter = CustomTextSplitter("\n\n")

# 2.加载文档并分割
documents = loader.load()
chucks = text_splitter.split_documents(documents)

# 3.循环遍历文档信息
for chuck in chucks:
    print(f"{chuck.page_content}\n")
