import os
from dotenv import load_dotenv
from src.agent.providers.model_provider import ModelProvider
from src.agent.providers.search_provider import SearchProvider
from src.agent.sentient_chat.interface.identity import Identity
from src.agent.sentient_chat.implementation.response_handler import ResponseHandler
from typing import Iterator


load_dotenv()


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
        response_handler = ResponseHandler(self._identity)
        # Rephrase query for better search results
        yield response_handler.create_text_event(
            "PLAN", "Rephrasing user query..."
        )
        rephrased_query = self.__rephrase_query(query)
        yield response_handler.create_text_event(
            event_name="REPHRASE",
            content=f"Rephrased query: {rephrased_query}"
        )

        # Search for information
        yield response_handler.create_text_event(
            "SEARCH", "Searching internet for results..."
        )
        search_results = self._search_provider.search(rephrased_query)
        if len(search_results["results"]) > 0:
            yield response_handler.create_json_event(
                "SOURCES", {"results": search_results["results"]}
            )
        if len(search_results["images"]) > 0:
            yield response_handler.create_json_event(
                "IMAGES", {"images": search_results["images"]}
            )

        # Process search results
        text_stream_handler = response_handler.create_text_stream_handler(
            event_name="FINAL_RESPONSE"
        )
        for chunk in self.__process_search_results(search_results["results"]):
            yield text_stream_handler.create_stream_chunk_event(chunk)
        yield text_stream_handler.create_stream_complete_event()
        yield response_handler.create_done_event()


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