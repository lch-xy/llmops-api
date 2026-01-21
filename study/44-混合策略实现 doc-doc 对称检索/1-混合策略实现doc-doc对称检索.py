#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/20 21:50
@Author  : LCH
@File   : 1-混合策略实现doc-doc对称检索.py
"""
import os

import dotenv
import weaviate
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()


class HyDERetriever(BaseRetriever):
    """HyDE混合策略检索器"""
    retriever: BaseRetriever
    llm: BaseLanguageModel

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        """传递检索query实现HyDE混合策略检索"""
        # 1.构建设个昵称假设性文档prompt
        prompt = ChatPromptTemplate.from_template(
            "请写一篇科学论文来回答这个问题。\n"
            "问题: {question}\n"
            "文章: "
        )

        # 2.构建HyDE混合策略检索链
        chain = (
                {"question": RunnablePassthrough()} |
                prompt |
                self.llm |
                StrOutputParser() |
                self.retriever
        )

        return chain.invoke(query)


# 1.构建向量数据库与检索器
db = WeaviateVectorStore(
    client=weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    ),
    index_name="Dataset",
    text_key="text",
    embedding=OllamaEmbeddings(model="embeddinggemma"),
)
retriever = db.as_retriever(search_type="mmr")

# 2,创建HyDE检索器
hyde_retriever = HyDERetriever(
    retriever=retriever,
    llm=ChatOpenAI(
        model="qwen3:8b",
        base_url=os.getenv("OPENAI_API_BASE_URL"),
        temperature=0
    )
)

# 3.检索文档
documents = hyde_retriever.invoke("关于LLMOps应用配置文档有哪些？")
print(documents)
print(len(documents))

db._client.close()
