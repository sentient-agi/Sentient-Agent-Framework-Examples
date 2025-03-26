import logging
import os
from dotenv import load_dotenv
from queue import Queue
from src.agent.providers.model_provider import ModelProvider
from src.agent.providers.search_provider import SearchProvider
from src.agent.sentient_agent.implementation.default_response_handler import DefaultResponseHandler
from src.agent.sentient_agent.implementation.default_hook import DefaultHook
from src.agent.sentient_agent.interface.identity import Identity
from typing import Iterator


load_dotenv()
logger = logging.getLogger(__name__)


class Agent:
    def __init__(
            self,
            identity: Identity,
            response_queue: Queue
    ):
        self._identity = identity
        self._response_queue = response_queue

        model_api_key=os.getenv("MODEL_API_KEY")
        if not model_api_key:
            raise ValueError("MODEL_API_KEY is not set")
        self._model_provider = ModelProvider(api_key=model_api_key)

        search_api_key=os.getenv("TAVILY_API_KEY")
        if not search_api_key:
            raise ValueError("TAVILY_API_KEY is not set") 
        self._search_provider = SearchProvider(api_key=search_api_key)


    async def search(
            self,
            query: str
    ):
        response_handler = DefaultResponseHandler(self._identity, DefaultHook(self._response_queue))
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