import os
import json
import logging
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any, Iterator

import httpx

logger = logging.getLogger("vertex_ai_stream")
logger.setLevel(logging.INFO)


class VertexAIStreamClient:
    """
    Asynchronous streaming client for Google Vertex AI Gemini (streamGenerateContent).

    - Без фреймворков (Django/ASGI, FastAPI, CLI).
    - Чистый SSE-парсинг с backpressure (aiter_lines).
    - Системка заточена под астрологию/науку.
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            model: str = "gemini-2.5-flash-lite",
            *,
            temperature: float = 0.8,
            top_p: float = 0.95,
            top_k: int = 40,
            max_output_tokens: int = 1024,
            request_timeout: Optional[float] = None,  # None = no overall timeout
    ) -> None:
        self.api_key = api_key or os.environ.get("VERTEX_API_KEY")
        if not self.api_key:
            raise RuntimeError("VERTEX_API_KEY is required")

        self.model = model
        # Важное: alt=sse даёт SSE-стримы
        # Док: publishers.models.streamGenerateContent — стримовый метод Vertex.  [oai_citation:1‡Google Cloud](https://cloud.google.com/vertex-ai/generative-ai/docs/reference/express-mode/rest/v1/publishers.models/streamGenerateContent)
        base = f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:streamGenerateContent"
        self.endpoint = f"{base}?key={self.api_key}&alt=sse"

        self.generation_config = {
            "temperature": temperature,
            "topP": top_p,
            "topK": top_k,
            "maxOutputTokens": max_output_tokens,
        }
        self._timeout = request_timeout

        self.system_prompt = (
            "You are an AI assistant specialized in astrology and related scientific fields "
            "(astronomy, physics). Provide accurate, concise, and insightful responses about these topics. "
            "When the user provides content (post/article), analyze it thoroughly or answer questions "
            "strictly based on that content. Maintain a professional, neutral tone. "
        )

    async def stream(
            self,
            *,
            query: Optional[str] = None,
            content: Optional[str] = None,
            task: str = "answer",                 # "answer" | "analyze"
            category: Optional[str] = None,
            description: Optional[str] = None,
            content_type: Optional[str] = None,   # "post" | "paper" | ...
            language: Optional[str] = None,       # "en" | "ru" | None=auto
            extra_labels: Optional[Dict[str, str]] = None,
            extra_config: Optional[Dict[str, Any]] = None,
            safety_settings: Optional[list] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Streams generated text chunks from Vertex AI Gemini.
        """
        payload = self._build_payload(
            query=query,
            content=content,
            task=task,
            category=category,
            description=description,
            content_type=content_type,
            language=language,
            extra_labels=extra_labels,
            extra_config=extra_config,
            safety_settings=safety_settings,
        )

        headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
        }

        # httpx aiter_lines → аккуратно читаем построчно без буферизации всего ответа
        async with httpx.AsyncClient(timeout=self._timeout, http2=True) as client:
            try:
                async with client.stream("POST", self.endpoint, json=payload, headers=headers) as resp:
                    resp.raise_for_status()

                    # SSE накопитель одного события (может состоять из нескольких data: строк)
                    event_lines: list[str] = []

                    async for raw_line in resp.aiter_lines():
                        if raw_line is None:
                            continue
                        line = raw_line.strip("\r\n")

                        # Комментарии SSE начинаются с ":" — игнорим
                        if not line:
                            # Пустая строка — конец события: склеиваем все data:
                            if not event_lines:
                                continue
                            data_blob = "\n".join(event_lines)
                            event_lines.clear()
                            # Каждый event — отдельный JSON объект GenerateContentResponse
                            obj = self._try_json(data_blob)
                            if obj is None:
                                continue
                            for text in self._extract_texts(obj):
                                if text:
                                    yield text
                            continue

                        if line.startswith("data:"):
                            # Берём все data: строки — по SSE они конкатенируются \n
                            event_lines.append(line[5:].lstrip())
                            continue

                        # Другие поля SSE (event:, id:, retry:) нам не нужны — пропускаем

            except httpx.HTTPStatusError as e:
                logger.error("Vertex HTTP error %s: %s", e.response.status_code, self._safe_text(e.response))
                raise
            except (httpx.ReadTimeout, httpx.WriteTimeout) as e:
                logger.error("Vertex timeout: %s", e)
                raise
            except asyncio.CancelledError:
                logger.warning("Stream cancelled by caller")
                raise
            except Exception as e:
                logger.exception("Unexpected streaming error: %s", e)
                raise

    # -------- internals --------

    def _build_payload(
            self,
            *,
            query: Optional[str],
            content: Optional[str],
            task: str,
            category: Optional[str],
            description: Optional[str],
            content_type: Optional[str],
            language: Optional[str],
            extra_labels: Optional[Dict[str, str]],
            extra_config: Optional[Dict[str, Any]],
            safety_settings: Optional[list],
    ) -> Dict[str, Any]:
        lang = (language or self._autodetect_language(query, content)).lower()
        require_ru = lang.startswith("ru")

        user_text = self._build_user_message(
            query=query,
            content=content,
            task=task,
            category=category,
            description=description,
            content_type=content_type,
            require_ru=require_ru,
        )

        payload: Dict[str, Any] = {
            "systemInstruction": {
                "role": "system",
                "parts": [{"text": self.system_prompt}],
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_text}]}
            ],
            "generationConfig": {**self.generation_config},
        }

        if extra_labels:
            payload["labels"] = extra_labels
        if extra_config:
            payload["generationConfig"].update(extra_config)
        if safety_settings:
            payload["safetySettings"] = safety_settings

        return payload

    def _build_user_message(
            self,
            *,
            query: Optional[str],
            content: Optional[str],
            task: str,
            category: Optional[str],
            description: Optional[str],
            content_type: Optional[str],
            require_ru: bool,
    ) -> str:
        lines = []
        if require_ru:
            lines.append("Ответь на русском языке.")

        meta = []
        if content_type:
            meta.append(f"type={content_type}")
        if category:
            meta.append(f"category={category}")
        if description:
            meta.append(f"description={description}")
        if meta:
            lines.append(f"[meta] {'; '.join(meta)}")

        if content:
            lines += ['Context:\n"""', content.strip(), '"""']

        if task == "analyze":
            lines.append("Task: Provide a concise analysis and summary strictly based on the context above.")
        else:
            lines.append("Task: Answer the question strictly based on the context if provided.")

        if query:
            lines.append(f"Question: {query.strip()}")

        return "\n".join(lines).strip()

    @staticmethod
    def _autodetect_language(query: Optional[str], content: Optional[str]) -> str:
        sample = (query or "") + " " + (content or "")
        for ch in sample:
            if "а" <= ch.lower() <= "я" or ch in "ёЁ":
                return "ru"
        return "en"

    @staticmethod
    def _try_json(data: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _extract_texts(chunk: Dict[str, Any]) -> Iterator[str]:
        """
        Vertex streamGenerateContent шлёт поток объектов GenerateContentResponse,
        внутри которых обычно candidates[0].content.parts[*].text
        """
        # Иногда приходит массив ответов
        if isinstance(chunk, list):
            for item in chunk:
                yield from VertexAIStreamClient._extract_texts(item)
            return

        cands = (chunk or {}).get("candidates") or []
        if not cands:
            return
        content = cands[0].get("content") or {}
        parts = content.get("parts") or []
        for p in parts:
            t = p.get("text")
            if t:
                yield t

    @staticmethod
    def _safe_text(resp: httpx.Response) -> str:
        try:
            return resp.text[:1000]
        except Exception:
            return "<unreadable>"
