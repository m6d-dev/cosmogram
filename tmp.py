import asyncio

from src.utils.vertex.client import VertexAIStreamClient

# logging.basicConfig(level=logging.DEBUG)

async def main():
    client = VertexAIStreamClient(api_key="AQ.Ab8RN6L-04Hk0tckcH1vzxNq1V6BKUQCXLnmB2vXdz1-DvEsvA")
    async for chunk in client.stream(
            query="Hello bro. What u can say about massive black wholes, like one in the milky way center?",
            task="ask",
            category="astrology",
            extra_config={"maxOutputTokens": 800},
    ):
        print(chunk, end="", flush=True)
asyncio.run(main())
