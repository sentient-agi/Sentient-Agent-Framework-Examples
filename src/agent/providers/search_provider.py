from tavily import TavilyClient

class SearchProvider:
    def __init__(
            self,
            api_key: str
    ):
        self.client = TavilyClient(api_key=api_key)


    def search(
            self,
            query: str
    ) -> dict:
        results = self.client.search(query)
        return results