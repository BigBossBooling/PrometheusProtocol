import httpx
from .llm_interface import LLMInterface

class GeminiAdapter(LLMInterface):
    """
    An adapter for the Google Gemini API.
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

    def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the Gemini API.

        Args:
            prompt: The prompt to send to the Gemini API.

        Returns:
            The response from the Gemini API.
        """
        if self.api_key == "YOUR_API_KEY":
            # Mock responses for the demo
            if "self_description" in prompt:
                return "I am Jules, a curious explorer."
            elif "generate_ideas" in prompt:
                return "Let's brainstorm some ideas for our next adventure!"
            else:
                return "I am not sure how to respond to that."

        headers = {"Content-Type": "application/json"}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": self.api_key}

        with httpx.Client() as client:
            response = client.post(self.api_url, headers=headers, json=data, params=params)
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
