import asyncio

class TextProcessor:
    """
    A class for processing text data.
    """

    async def tokenize(self, data: str) -> list[str]:
        """
        Tokenizes text data.

        Args:
            data: The text data to tokenize.

        Returns:
            A list of tokens.
        """
        print("Tokenizing text data...")
        await asyncio.sleep(1)  # Simulate processing
        return data.split()

    async def clean(self, tokens: list[str]) -> list[str]:
        """
        Cleans text data.

        Args:
            tokens: The tokens to clean.

        Returns:
            A list of cleaned tokens.
        """
        print("Cleaning text data...")
        await asyncio.sleep(1)  # Simulate processing
        return [token.lower() for token in tokens]
