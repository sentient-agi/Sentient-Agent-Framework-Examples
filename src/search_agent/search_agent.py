import logging
import os
from dotenv import load_dotenv
from src.search_agent.providers.model_provider import ModelProvider
from src.search_agent.providers.search_provider import SearchProvider
from sentient_agent_framework import (
    BaseAgent,
    Identity,
    Session,
    Query,
    ResponseHandler)
from typing import Iterator


load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SearchAgent(BaseAgent):
    def __init__(
            self,
            identity: Identity
    ):
        super().__init__(identity)

        model_api_key = os.getenv("MODEL_API_KEY")
        if not model_api_key:
            raise ValueError("MODEL_API_KEY is not set")
        self._model_provider = ModelProvider(api_key=model_api_key)

        search_api_key = os.getenv("TAVILY_API_KEY")
        if not search_api_key:
            raise ValueError("TAVILY_API_KEY is not set") 
        self._search_provider = SearchProvider(api_key=search_api_key)


    async def assist(
            self,
            session: Session,
            query: Query,
            response_handler: ResponseHandler
    ):
        """Search the internet for information."""
        # Rephrase query for better search results
        await response_handler.emit_text_block(
            "PLAN", "Rephrasing user query..."
        )
        rephrased_query = self.__rephrase_query(query)
        await response_handler.emit_text_block(
            "REPHRASE", f"Rephrased query: {rephrased_query}"
        )

        # Search for information
        await response_handler.emit_text_block(
            "SEARCH", "Searching internet for results..."
        )
        search_results = self._search_provider.search(rephrased_query)
        if len(search_results["results"]) > 0:
            await response_handler.emit_json(
                "SOURCES", {"results": search_results["results"]}
            )
        if len(search_results["images"]) > 0:
            await response_handler.emit_json(
                "IMAGES", {"images": search_results["images"]}
            )

        # Process search results
        final_response_stream = response_handler.create_text_stream(
            "FINAL_RESPONSE"
            )
        for chunk in self.__process_search_results(search_results["results"]):
            await final_response_stream.emit_chunk(chunk)
        await final_response_stream.complete()
        await response_handler.complete()


    def __rephrase_query(
            self,
            query: str
    ) -> str:
        """Rephrase the query for better search results."""
        rephrase_query = f"Rephrase the following query for better search results: {query}"
        rephrase_query_response = self._model_provider.query(rephrase_query)
        return rephrase_query_response
    

    def __process_search_results(
            self, 
            search_results: dict
    ) -> Iterator[str]:
        """Process the search results."""
        process_search_results_query = f"Summarise the following search results: {search_results}"
        for chunk in self._model_provider.query_stream(process_search_results_query):
            yield chunk


if __name__ == "__main__":
    agent = SearchAgent(identity=Identity(id="Search-Demo", name="Search Demo"))
    agent.run_server()