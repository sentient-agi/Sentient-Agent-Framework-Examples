from dotenv import load_dotenv
from flask import Flask, Response, request
from src.agent.providers.model_provider import ModelProvider
from src.agent.providers.search_provider import SearchProvider
from src.agent.sentient_chat.implementation.SSE_response_handler import SSEResponseHandler
import asyncio
import os

load_dotenv()
class Agent:
    def __init__(self, response_queue):
        self.model_provider = ModelProvider(api_key=os.getenv("MODEL_API_KEY"))
        self.search_provider = SearchProvider(api_key=os.getenv("TAVILY_API_KEY"))
        self.response_queue = response_queue
        self.response_handler = SSEResponseHandler(self.response_queue)


    async def search(self, query):
        # Rephrase query for better search results
        await self.response_handler.emit_text_block(
            "PLAN", "Rephrasing user query..."
        )
        print("Rephrasing user query...")
        rephrased_query = self.rephrase_query(query)
        await self.response_handler.emit_text_block(
            "REPHRASE", f"Rephrased query: {rephrased_query}"
        )
        print(f"Rephrased query: {rephrased_query}")

        # Search for information
        await self.response_handler.emit_text_block(
            "SEARCH", "Searching internet for results..."
        )
        print("Searching internet for results...")
        search_results = self.search_provider.search(rephrased_query)
        print(f"Search results: {search_results}")
        if len(search_results["results"]) > 0:
            await self.response_handler.emit_json(
                "SOURCES", {"results": search_results["results"]}
            )
        if len(search_results["images"]) > 0:
            await self.response_handler.emit_json(
                "IMAGES", {"images": search_results["images"]}
            )

        # Process search results
        final_response_stream = self.response_handler.create_text_stream(
            "FINAL_RESPONSE"
            )
        print("Processing search results...")
        for chunk in self.process_search_results(search_results["results"]):
            await final_response_stream.emit_chunk(chunk)
        print("Final response stream complete, completing stream...")
        await final_response_stream.complete()
        print("Response complete, completing response handler...")
        await self.response_handler.complete()


    def rephrase_query(self, query):
        # Rephrase query for better search results
        rephrase_query = f"Rephrase the following query for better search results: {query}"
        rephrase_query_response = self.model_provider.query(rephrase_query)
        return rephrase_query_response
    

    def process_search_results(self, search_results):
        # Process search results
        process_search_results_query = f"Summarise the following search results: {search_results}"
        for chunk in self.model_provider.query_stream(process_search_results_query):
            yield chunk