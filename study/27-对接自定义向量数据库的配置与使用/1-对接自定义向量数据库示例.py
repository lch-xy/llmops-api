#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/2 16:40
@Author  : LCH
@File   : 1-对接自定义向量数据库示例.py
"""
import uuid
from typing import Any, Iterable, Optional, List

import dotenv
import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_ollama import OllamaEmbeddings


class MemoryVectorStore(VectorStore):
    """基于内存+欧几里得距离的向量数据库"""
    store: dict = {}

    def __init__(self, embedding: Embeddings):
        self._embedding = embedding

    def add_texts(self, texts: Iterable[str], metadatas: Optional[List[dict]] = None, **kwargs: Any) -> List[str]:
        """将数据库添加动啊内存向量数据库中"""
        # 1.判断metadatas和texts的长度是否保持一致
        if metadatas is not None and len(metadatas) != len(texts):
            raise ValueError("元数据格式必须和文本格式保持一致")

        # 2.将文本转化为向量
        embeddings = self._embedding.embed_documents(texts)

        # 3.生成UUID
        ids = [str(uuid.uuid4()) for text in texts]

        # 4.将原始文本。向量、元数据、id构建字典并存储
        for idx, text in enumerate(texts):
            self.store[ids[idx]] = {
                "id": ids[idx],
                "vector": embeddings[idx],
                "text": text,
                "metadata": metadatas[idx] if metadatas is not None else {}
            }

        return ids

    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> list[Document]:
        """执行相似性搜索"""
        # 1.将query转化成向量
        embedding = self._embedding.embed_query(query)

        # 2.循环遍历记忆存储，计算欧几里得距离
        result: list = []
        for key, record in self.store.items():
            distance = self._euclidean_distance(embedding, record["vector"])
            # 合并结果
            result.append({
                "distance": distance,
                **record,
            })

        # 3.找到欧几里得距离最小的k条记录
        sorted_result = sorted(result, key=lambda x: x["distance"])
        result_k = sorted_result[:k]

        # 4.循环构建文档列表并返回
        documents = [
            Document(
                page_content=item["text"],
                metadatas={**item["metadata"], "score": item["distance"]}
            ) for item in result_k
        ]

        return documents

    @classmethod
    def from_texts(cls: type["MemoryVectorStore"], texts: list[str], embedding: Embeddings,
                   metadatas: list[dict] = None,
                   **kwargs: Any) -> "MemoryVectorStore":
        """通过文本、嵌入模型、元数据构建向量数据库"""
        memory_vector_store = cls(embedding=embedding, **kwargs)
        memory_vector_store.add_texts(texts, metadatas)
        return memory_vector_store

    @classmethod
    def _euclidean_distance(cls, vec1, vec2) -> float:
        """计算两个向量的欧几里得距离"""
        return np.linalg.norm(np.array(vec1) - np.array(vec2))


dotenv.load_dotenv()

texts: list = [
    "笨笨是一只很喜欢睡觉的猫咪",
    "我喜欢在夜晚听音乐，这让我感到放松。",
    "猫咪在窗台上打盹，看起来非常可爱。",
    "学习新技能是每个人都应该追求的目标。",
    "我最喜欢的食物是意大利面，尤其是番茄酱的那种。",
    "昨晚我做了一个奇怪的梦，梦见自己在太空飞行。",
    "我的手机突然关机了，让我有些焦虑。",
    "阅读是我每天都会做的事情，我觉得很充实。",
    "他们一起计划了一次周末的野餐，希望天气能好。",
    "我的狗喜欢追逐球，看起来非常开心。",
]
metadatas: list = [
    {"page": 1},
    {"page": 2},
    {"page": 3},
    {"page": 4},
    {"page": 5},
    {"page": 6, "account_id": 1},
    {"page": 7},
    {"page": 8},
    {"page": 9},
    {"page": 10},
]

# embedding = OllamaEmbeddings(model="embeddinggemma")
#
# db = MemoryVectorStore.from_texts(texts, embedding, metadatas)
#
# print(db.similarity_search("我养了一只猫，叫笨笨"))
# print(db.similarity_search("笨笨是谁"))

# 2.构建自定义向量数据库
embedding = OllamaEmbeddings(model="embeddinggemma")
db = MemoryVectorStore(embedding=embedding)

ids = db.add_texts(texts, metadatas)
print(ids)

# 3.执行检索
print(db.similarity_search("笨笨是谁？"))
