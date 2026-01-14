#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time   : 2026/1/13 13:18
@Author  : LCH
@File   : OllamaTransformer.py
"""
from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

from langchain_core.documents import Document
from langchain_ollama import ChatOllama

try:
    # ollama python sdk error type (langchain_ollama uses it internally)
    from ollama._types import ResponseError
except Exception:  # pragma: no cover
    ResponseError = Exception  # fallback

_JSON_FENCE_RE = re.compile(r"```(?:json)?|```", re.IGNORECASE)
_JSON_OBJ_OR_ARR_RE = re.compile(r"(\[\s*{.*?}\s*]|\{.*\})", re.DOTALL)


def _strip_json_fences(text: str) -> str:
    """Remove ```json fences and surrounding noise."""
    return _JSON_FENCE_RE.sub("", text).strip()


def _extract_json_block(text: str) -> str:
    """
    Extract the first JSON object/array from a model response.
    This is robust to extra explanation text before/after JSON.
    """
    cleaned = _strip_json_fences(text)
    m = _JSON_OBJ_OR_ARR_RE.search(cleaned)
    return m.group(1).strip() if m else cleaned


def _safe_json_loads(text: str) -> Any:
    raw = _extract_json_block(text)
    return json.loads(raw)


@dataclass
class OllamaQATransformer:
    """
    Doctran-like QA transformer using Ollama chat model.

    Output style (doctran-like):
      - For each input Document, output one Document
      - Keep original page_content
      - Put extracted QAs into metadata["questions_and_answers"] as a list[dict]
    """

    model: str = "qwen3:8b"
    base_url: Optional[str] = None  # e.g. "http://127.0.0.1:11434"
    temperature: float = 0.1

    max_qas_per_doc: int = 6
    min_answer_chars: int = 10

    # Retry for transient 503 etc.
    max_retries: int = 6
    retry_backoff_base_seconds: float = 1.5
    retry_backoff_cap_seconds: float = 20.0

    # Async concurrency
    concurrency: int = 4

    def _llm(self) -> ChatOllama:
        kwargs: Dict[str, Any] = {"model": self.model, "temperature": self.temperature}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return ChatOllama(**kwargs)

    def _build_messages(self, text: str) -> List[Dict[str, str]]:
        """
        JSON-only output to ease parsing and reduce hallucinations.
        """
        system = (
            "你是一个“基于原文抽取问答”的信息抽取器。\n"
            "任务：仅基于给定原文，生成用户可能会问的问题及其答案。\n"
            "硬性要求：\n"
            "1) 只能使用原文中明确给出的信息作答，禁止推测、禁止扩展常识。\n"
            "2) 输出必须是严格 JSON（不要 markdown、不要解释性文字）。\n"
            "3) 如果原文无法支撑某个问题的答案，就不要生成该问题。\n"
            "4) 问题要贴近用户真实提问（问句），答案简洁准确。\n"
            f"5) 最多生成 {self.max_qas_per_doc} 条。\n\n"
            "输出 JSON 数组格式如下：\n"
            "[\n"
            "  {\n"
            '    "question": "…",\n'
            '    "answer": "…",\n'
            '    "evidence": "支持该答案的原文片段（尽量原句）",\n'
            '    "confidence": 0.0\n'
            "  }\n"
            "]\n"
            "confidence 范围 0~1（越接近1表示原文越明确支持）。"
        )

        user = (
            "原文如下（只允许基于它作答）：\n"
            "-----\n"
            f"{text}\n"
            "-----"
        )

        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def _invoke_with_retry(self, llm: ChatOllama, messages: Sequence[Dict[str, str]]) -> str:
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                resp = llm.invoke(list(messages))
                return getattr(resp, "content", str(resp))
            except Exception as e:
                last_err = e
                # only retry transient 503; other errors raise directly
                status_code = getattr(e, "status_code", None)
                # ollama ResponseError stores status_code; sometimes nested
                if isinstance(e, ResponseError):
                    status_code = getattr(e, "status_code", status_code)

                if status_code not in (503,):
                    raise

                sleep_s = min(self.retry_backoff_base_seconds ** attempt, self.retry_backoff_cap_seconds)
                time.sleep(sleep_s)

        raise RuntimeError(f"Ollama chat failed after retries. Last error: {last_err}") from last_err

    def _parse_qas(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse model output JSON -> list[qa dict], then sanitize and filter.
        """
        try:
            data = _safe_json_loads(content)
        except Exception:
            return []

        if not isinstance(data, list):
            return []

        qas: List[Dict[str, Any]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            q = str(item.get("question", "")).strip()
            a = str(item.get("answer", "")).strip()
            ev = str(item.get("evidence", "")).strip()
            conf = item.get("confidence", None)

            if not q or not a:
                continue
            if len(a) < self.min_answer_chars:
                continue

            # normalize confidence
            try:
                conf_f = float(conf) if conf is not None else None
                if conf_f is not None:
                    conf_f = max(0.0, min(1.0, conf_f))
            except Exception:
                conf_f = None

            qas.append(
                {
                    "question": q,
                    "answer": a,
                    "evidence": ev,
                    "confidence": conf_f,
                }
            )

            if len(qas) >= self.max_qas_per_doc:
                break

        return qas

    def _transform_one(self, doc: Document) -> Document:
        llm = self._llm()
        messages = self._build_messages(doc.page_content)
        content = self._invoke_with_retry(llm, messages)
        qas = self._parse_qas(content)

        meta = dict(doc.metadata or {})
        meta["questions_and_answers"] = qas  # ALWAYS list (never None)
        meta["qa_transformer"] = "OllamaQATransformer"
        meta["qa_model"] = self.model

        # 保留原文 page_content（更方便溯源）
        return Document(page_content=doc.page_content, metadata=meta)

    def transform_documents(self, documents: List[Document]) -> List[Document]:
        """Sync API: doctran-like."""
        return [self._transform_one(doc) for doc in documents]

    async def _ainvoke_with_retry(self, llm: ChatOllama, messages: Sequence[Dict[str, str]]) -> str:
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                resp = await llm.ainvoke(list(messages))
                return getattr(resp, "content", str(resp))
            except Exception as e:
                last_err = e
                status_code = getattr(e, "status_code", None)
                if isinstance(e, ResponseError):
                    status_code = getattr(e, "status_code", status_code)

                if status_code not in (503,):
                    raise

                sleep_s = min(self.retry_backoff_base_seconds ** attempt, self.retry_backoff_cap_seconds)
                await asyncio.sleep(sleep_s)

        raise RuntimeError(f"Ollama chat failed after retries. Last error: {last_err}") from last_err

    async def _transform_one_async(self, doc: Document, sem: asyncio.Semaphore) -> Document:
        async with sem:
            llm = self._llm()
            messages = self._build_messages(doc.page_content)
            content = await self._ainvoke_with_retry(llm, messages)
            qas = self._parse_qas(content)

            meta = dict(doc.metadata or {})
            meta["questions_and_answers"] = qas
            meta["qa_transformer"] = "OllamaQATransformer"
            meta["qa_model"] = self.model
            return Document(page_content=doc.page_content, metadata=meta)

    async def atransform_documents(self, documents: List[Document]) -> List[Document]:
        """Async API with concurrency."""
        sem = asyncio.Semaphore(self.concurrency)
        tasks = [self._transform_one_async(doc, sem) for doc in documents]
        return await asyncio.gather(*tasks)


@dataclass
class OllamaTextTranslator:
    """
    DoctranTextTranslator-like translator using an Ollama chat model.

    - Translates Document.page_content into target_language.
    - Optionally stores original text in metadata.
    - Optionally translates selected metadata fields.
    - Provides sync + async APIs with retry for transient 503.
    """

    model: str = "qwen3:8b"
    base_url: Optional[str] = None  # e.g. "http://127.0.0.1:11434"
    temperature: float = 0.0

    source_language: str = "auto"  # "auto" | "zh" | "en" ...
    target_language: str = "zh"  # "zh" | "en" ...

    # behavior
    preserve_original: bool = True
    add_language_metadata: bool = True

    # translate specific metadata keys (e.g. ["title", "section"])
    translate_metadata_keys: Optional[List[str]] = None

    # retry for transient errors
    max_retries: int = 6
    retry_backoff_base_seconds: float = 1.5
    retry_backoff_cap_seconds: float = 20.0

    # async concurrency
    concurrency: int = 4

    def _llm(self) -> ChatOllama:
        kwargs: Dict[str, Any] = {"model": self.model, "temperature": self.temperature}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return ChatOllama(**kwargs)

    def _build_messages(self, text: str) -> List[Dict[str, str]]:
        """
        IMPORTANT:
          - Force "translation only" output: no explanations, no quotes.
          - Keep formatting (line breaks, lists, code blocks).
        """
        system = (
            "你是一个专业翻译器。\n"
            "要求：只输出翻译结果，不要解释、不要加引号、不要添加额外内容。\n"
            "尽量保持原始格式（换行、列表、标点、代码块）。\n"
            "对于专有名词/接口名/代码/URL，请保持原样。\n"
        )

        user = (
            f"请把下面文本从 {self.source_language} 翻译成 {self.target_language}。\n"
            "只输出译文：\n"
            "-----\n"
            f"{text}\n"
            "-----"
        )
        return [{"role": "system", "content": system}, {"role": "user", "content": user}]

    def _invoke_with_retry(self, llm: ChatOllama, messages: Sequence[Dict[str, str]]) -> str:
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                resp = llm.invoke(list(messages))
                return getattr(resp, "content", str(resp)).strip()
            except Exception as e:
                last_err = e
                status_code = getattr(e, "status_code", None)
                if isinstance(e, ResponseError):
                    status_code = getattr(e, "status_code", status_code)

                if status_code not in (503,):
                    raise

                sleep_s = min(self.retry_backoff_base_seconds ** attempt, self.retry_backoff_cap_seconds)
                time.sleep(sleep_s)

        raise RuntimeError(f"Ollama translate failed after retries. Last error: {last_err}") from last_err

    async def _ainvoke_with_retry(self, llm: ChatOllama, messages: Sequence[Dict[str, str]]) -> str:
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                resp = await llm.ainvoke(list(messages))
                return getattr(resp, "content", str(resp)).strip()
            except Exception as e:
                last_err = e
                status_code = getattr(e, "status_code", None)
                if isinstance(e, ResponseError):
                    status_code = getattr(e, "status_code", status_code)

                if status_code not in (503,):
                    raise

                sleep_s = min(self.retry_backoff_base_seconds ** attempt, self.retry_backoff_cap_seconds)
                await asyncio.sleep(sleep_s)

        raise RuntimeError(f"Ollama translate failed after retries. Last error: {last_err}") from last_err

    def _translate_text(self, llm: ChatOllama, text: str) -> str:
        if text is None:
            return ""
        text = str(text)
        if not text.strip():
            return text
        messages = self._build_messages(text)
        return self._invoke_with_retry(llm, messages)

    async def _atranslate_text(self, llm: ChatOllama, text: str) -> str:
        if text is None:
            return ""
        text = str(text)
        if not text.strip():
            return text
        messages = self._build_messages(text)
        return await self._ainvoke_with_retry(llm, messages)

    def _transform_one(self, doc: Document) -> Document:
        llm = self._llm()

        original = doc.page_content
        translated = self._translate_text(llm, original)

        meta = dict(doc.metadata or {})
        if self.preserve_original:
            meta["original_page_content"] = original

        if self.add_language_metadata:
            meta["translated_from"] = self.source_language
            meta["translated_to"] = self.target_language
            meta["translator"] = "OllamaTextTranslator"
            meta["translator_model"] = self.model

        # Optionally translate some metadata fields (strings only)
        if self.translate_metadata_keys:
            for k in self.translate_metadata_keys:
                v = meta.get(k)
                if isinstance(v, str) and v.strip():
                    meta[k] = self._translate_text(llm, v)

        return Document(page_content=translated, metadata=meta)

    def transform_documents(self, documents: List[Document]) -> List[Document]:
        """Sync translate."""
        return [self._transform_one(doc) for doc in documents]

    async def _transform_one_async(self, doc: Document, sem: asyncio.Semaphore) -> Document:
        async with sem:
            llm = self._llm()

            original = doc.page_content
            translated = await self._atranslate_text(llm, original)

            meta = dict(doc.metadata or {})
            if self.preserve_original:
                meta["original_page_content"] = original

            if self.add_language_metadata:
                meta["translated_from"] = self.source_language
                meta["translated_to"] = self.target_language
                meta["translator"] = "OllamaTextTranslator"
                meta["translator_model"] = self.model

            if self.translate_metadata_keys:
                for k in self.translate_metadata_keys:
                    v = meta.get(k)
                    if isinstance(v, str) and v.strip():
                        meta[k] = await self._atranslate_text(llm, v)

            return Document(page_content=translated, metadata=meta)

    async def atransform_documents(self, documents: List[Document]) -> List[Document]:
        """Async translate with concurrency."""
        sem = asyncio.Semaphore(self.concurrency)
        tasks = [self._transform_one_async(doc, sem) for doc in documents]
        return await asyncio.gather(*tasks)
