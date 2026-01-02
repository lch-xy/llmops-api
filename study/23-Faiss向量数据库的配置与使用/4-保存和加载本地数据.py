#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/2 11:55
@Author  : LCH
@File   : 4-保存和加载本地数据.py
"""
import os

import dotenv
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
dotenv.load_dotenv()

embedding = OllamaEmbeddings(model="embeddinggemma")
#
# db = FAISS.from_texts(
#     ["笨笨是一只很喜欢睡觉的猫咪", "我喜欢在夜晚听音乐,这让我感到放松。", "猫咪在窗台上打盹,看起来非常可爱。",
#      "学习新技能是每个人都应该追求的目标。", "我最喜欢的食物是意大利面,尤其是番茄酱的那种。",
#      "昨晚我做了一个奇怪的梦,梦见自己在太空飞行。", "我的手机突然关机了,让我有些焦虑。",
#      "阅读是我每天都会做的事情,我觉得很充实。", "他们一起计划了一次周末的野餐,希望天气能好。",
#      "我的狗喜欢追逐球,看起来非常开心。", ], embedding, relevance_score_fn=lambda distance: 1.0 / (1.0 + distance))
#
# db.save_local("faiss_index")
new_db = FAISS.load_local(
    "faiss_index",
    embedding,
    allow_dangerous_deserialization=True,  # 信任数据库
)
docs = new_db.similarity_search("我养了一只猫，叫笨笨")

print(docs)
