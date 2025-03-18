import logging
import os
from dotenv import load_dotenv
from queue import Queue
from src.agent.providers.model_provider import ModelProvider
from src.agent.providers.search_provider import SearchProvider
from .sentient_chat.events import (
    DocumentEvent,
    TextBlockEvent,
    DoneEvent
)
from .sentient_chat.identity import Identity
from .sentient_chat.text_stream import TextStream
from typing import Iterator


load_dotenv()
logger = logging.getLogger(__name__)


class Agent:
    def __init__(
            self,
            identity: Identity
    ):
        self._identity = identity
        self._model_provider = ModelProvider(api_key=os.getenv("MODEL_API_KEY"))
        self._search_provider = SearchProvider(api_key=os.getenv("TAVILY_API_KEY"))


    def search(
            self,
            query: str
    ):
        # Rephrase query for better search results
        yield TextBlockEvent(
            source=self._identity.id,
            event_name="PLAN",
            content="Rephrasing user query..."
        )
        logger.info("Rephrasing user query...")
        rephrased_query = self.__rephrase_query(query)
        yield TextBlockEvent(
            source=self._identity.id,
            event_name="REPHRASE",
            content=f"Rephrased query: {rephrased_query}"
        )
        logger.info(f"Rephrased query: {rephrased_query}")

        # Search for information
        yield TextBlockEvent(
            source=self._identity.id,
            event_name="SEARCH",
            content="Searching internet for results..."
        )
        logger.info("Searching internet for results...")
        search_results = self._search_provider.search(rephrased_query)
        logger.info(f"Search results: {search_results}")
        if len(search_results["results"]) > 0:
            yield DocumentEvent(
                source=self._identity.id,
                event_name="SOURCES",
                content={"results": search_results["results"]}
            )
        if len(search_results["images"]) > 0:
            yield DocumentEvent(
                source=self._identity.id,
                event_name="IMAGES",
                content={"images": search_results["images"]}
            )

        # Process search results
        final_response_stream = TextStream(
            event_source=self._identity,
            event_name="FINAL_RESPONSE"
        )
        logger.info("Processing search results...")
        for chunk in self.__process_search_results(search_results["results"]):
            yield final_response_stream.create_chunk(chunk)
        logger.info("Final response stream complete, completing stream...")
        yield final_response_stream.complete()
        logger.info("Response complete, completing response handler...")
        yield DoneEvent(
            source=self._identity.id
        )


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