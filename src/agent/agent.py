import logging
import os
from dotenv import load_dotenv
from queue import Queue
from src.agent.providers.model_provider import ModelProvider
from src.agent.providers.search_provider import SearchProvider
from src.agent.sentient_chat.implementation.queue_response_handler import QueueResponseHandler
from src.agent.sentient_chat.interface.identity import Identity
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
        self._response_handler = QueueResponseHandler(self._identity, self._response_queue)
        self._model_provider = ModelProvider(api_key=os.getenv("MODEL_API_KEY"))
        self._search_provider = SearchProvider(api_key=os.getenv("TAVILY_API_KEY"))


    async def search(
            self,
            query: str
    ):
        # Rephrase query for better search results
        await self._response_handler.emit_text_block(
            "PLAN", "Rephrasing user query..."
        )
        logger.info("Rephrasing user query...")
        rephrased_query = self.__rephrase_query(query)
        await self._response_handler.emit_text_block(
            "REPHRASE", f"Rephrased query: {rephrased_query}"
        )
        logger.info(f"Rephrased query: {rephrased_query}")

        # Search for information
        await self._response_handler.emit_text_block(
            "SEARCH", "Searching internet for results..."
        )
        logger.info("Searching internet for results...")
        search_results = self._search_provider.search(rephrased_query)
        logger.info(f"Search results: {search_results}")
        if len(search_results["results"]) > 0:
            await self._response_handler.emit_json(
                "SOURCES", {"results": search_results["results"]}
            )
        if len(search_results["images"]) > 0:
            await self._response_handler.emit_json(
                "IMAGES", {"images": search_results["images"]}
            )

        # Process search results
        final_response_stream = self._response_handler.create_text_stream(
            "FINAL_RESPONSE"
            )
        logger.info("Processing search results...")
        for chunk in self.__process_search_results(search_results["results"]):
            await final_response_stream.emit_chunk(chunk)
        logger.info("Final response stream complete, completing stream...")
        await final_response_stream.complete()
        logger.info("Response complete, completing response handler...")
        await self._response_handler.complete()


    def __rephrase_query(
            self,
            query: str
    ) -> str:
        # Rephrase query for better search results
        rephrase_query = f"Rephrase the following query for better search results: {query}"
        rephrase_query_response = self._model_provider.query(rephrase_query)
        return rephrase_query_response
    

    def __process_search_results(
            self, 
            search_results: dict
    ) -> Iterator[str]:
        # Process search results
        process_search_results_query = f"Summarise the following search results: {search_results}"
        for chunk in self._model_provider.query_stream(process_search_results_query):
            yield chunk