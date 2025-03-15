import openai
from datetime import datetime
from langchain_core.prompts import PromptTemplate


class ModelProvider:
    def __init__(self, api_key):
        """ Initializes model, sets up OpenAI client, configures system prompt."""

        # Model provider API key
        self.api_key = api_key
        # Model provider URL
        self.base_url = "https://api.fireworks.ai/inference/v1" 
        # Identifier for specific model that should be used
        self.model = "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new"
        # Temperature setting for response randomness
        self.temperature = 0.0
        # Maximum number of tokens for responses
        self.max_tokens = None
        self.system_prompt = "default"
        self.date_context = datetime.now().strftime("%Y-%m-%d")

        # Set up model API
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

        # Set up system prompt
        if self.system_prompt == "default":
            system_prompt_search = PromptTemplate(
                input_variables=["date_today"],
                template="You are a helpful assistant that can answer questions and provide information."
                )
            self.system_prompt = system_prompt_search.format(date_today=self.date_context)
        else:
            self.system_prompt = self.system_prompt


    def query_stream(self, query):
        """Sends query to model and yields the response in chunks."""
        if self.model in ["o1-preview", "o1-mini"]:
            messages = [
                {"role": "user",
                 "content": f"System Instruction: {self.system_prompt} \n Instruction:{query}"}
            ]
        else:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query}
            ]

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


    def query(self, query):
        """Sends query to model and returns the complete response as a string."""
        chunks = []
        for chunk in self.query_stream(query=query):
            chunks.append(chunk)
        response = "".join(chunks)
        return response
