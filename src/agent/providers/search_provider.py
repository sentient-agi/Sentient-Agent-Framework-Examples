from tavily import TavilyClient

class SearchProvider:
    def __init__(self, api_key):
        self.client = TavilyClient(api_key=api_key)

    def search(self, query):
        results = self.client.search(query)
        return results