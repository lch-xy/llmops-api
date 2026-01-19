#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/19 19:25
@Author  : LCH
@File   : 1-RAG多查询结果融合策略.py
"""

import os

import dotenv
import weaviate
from langchain_classic.retrievers import MultiQueryRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.load import dumps, loads
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_weaviate import WeaviateVectorStore

dotenv.load_dotenv()


class RAGFusionRetriever(MultiQueryRetriever):
    """RAG多查询结果融合检索器"""
    k: int = 4

    def __init__(self, k: int = 4, **kwargs):
        super().__init__(**kwargs)
        self.k = k

    def retrieve_documents(
            self,
            queries: list[str],
            run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        """重写检索文档，返回二层嵌套的列表"""
        documents = []
        for query in queries:
            docs = self.retriever.invoke(
                query,
                config={"callbacks": run_manager.get_child()}
            )
            documents.append(docs)
        return documents

    def unique_union(self, documents: list[Document]) -> list[Document]:
        """使用RRF算法对文档列表进行排序&合并"""
        # 1.初始化一个字典，用于存储没一个唯一文档的分
        fused_result = {}

        # 2.遍历每个查询对应的文档列表
        for docs in documents:
            # 3.内层遍历文档列表得到每一个文档
            for rank, doc in enumerate(docs):
                # 4.将文档使用langchain提供的dump工具转换为字符串
                doc_str = dumps(doc)
                # 5.检测该字符串是否存在得分，如果不存在则赋值为0
                if doc_str not in fused_result:
                    fused_result[doc_str] = 0
                # 6.计算多结果得分，排名余额小越靠前，k为控制权重的参数
                fused_result[doc_str] += 1 / (rank + 60)

        # 7.提取得分并进行排序
        reranked_results = [
            (loads(doc), score)
            for doc, score in sorted(fused_result.items(), key=lambda x: x[1], reverse=True)
        ]

        return [item[0] for item in reranked_results[:self.k]]


# 1.构建向量数据库检索器
db = WeaviateVectorStore(
    client=weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=os.getenv("WEAVIATE_API_KEY"),
    ),
    index_name="Dataset",
    text_key="text",
    embedding=OllamaEmbeddings(model="embeddinggemma")
)
retriever = db.as_retriever(search_type="mmr")

# 2.创建多查询检索器
multi_query_retriever = RAGFusionRetriever.from_llm(retriever=retriever,
                                                    llm=ChatOpenAI(model="qwen3:8b",
                                                                   base_url=os.getenv("OPENAI_API_BASE_URL"),
                                                                   temperature=0),
                                                    include_original=True)

# 3.执行检索
docs = multi_query_retriever.invoke("我的猫咪喜欢干嘛")
print(docs)
print(len(docs))

db._client.close()
