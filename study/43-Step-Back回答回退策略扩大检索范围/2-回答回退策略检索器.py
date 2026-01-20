#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/20 20:27
@Author  : LCH
@File   : 2-回答回退策略检索器.py
"""
import os

import dotenv
import weaviate
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.language_models import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_weaviate import WeaviateVectorStore
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()


class StepBackRetriever(BaseRetriever):
    """回答回退检索器"""
    retriever: BaseRetriever
    llm: BaseLanguageModel

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        """根据传递的query执行问题回退并检索"""
        # 1.构建少量示例提示模板
        examples = [
            {"input": "慕课网上有关于AI应用开发的课程吗？", "output": "慕课网上有哪些课程？"},
            {"input": "慕小课出生在哪个国家？", "output": "慕小课的人生经历是什么样的？"},
            {"input": "司机可以开快车吗？", "output": "司机可以做什么？"},
        ]
        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("ai", "{output}"),
        ])
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=examples,
            example_prompt=example_prompt
        )

        # 2.构建生成回退问题的模板
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "你是一个世界知识的专家。你的任务是回退问题，将问题改述为更一般或者前置问题，这样更容易回答。"
             "请严格参考示例，只输出一个回退后的问题，不要解释，不要换行，不要加前缀。"),
            few_shot_prompt,
            ("human", "{question}"),
        ])

        # 3.构建应用链，生成回退问题，并执行响应的检索
        chain = (
                {"question": RunnablePassthrough()} |
                prompt |
                self.llm |
                StrOutputParser() |
                self.retriever
        )

        return chain.invoke(query)


# 1.构建向量数据库
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

# 2.创建回答回退检索器
step_back_retriever = StepBackRetriever(
    retriever=retriever,
    llm=ChatOpenAI(model="qwen3:8b",
                   base_url=os.getenv("OPENAI_API_BASE_URL"),
                   temperature=0)
)

# 3.检索文档
documents = step_back_retriever.invoke("LLM是个什么东西？")
print(documents)
print(len(documents))

db._client.close()
