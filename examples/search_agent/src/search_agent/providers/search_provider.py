from tavily import AsyncTavilyClient

class SearchProvider:
    def __init__(
            self,
            api_key: str
    ):
        self.client = AsyncTavilyClient(api_key=api_key)


    async def search(
            self,
            query: str
    ) -> dict:
        results = await self.client.search(query)
        return results