from typing import AsyncIterator

from src.utils.vertex.client import VertexAIStreamClient


class VertexService:
    def __init__(self, client: VertexAIStreamClient):
        self.client = client

    async def ask_about_post(self, post_id) -> AsyncIterator[str] | None:
        stream = await self.client.stream(

        )
