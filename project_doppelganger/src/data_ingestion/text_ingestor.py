import asyncio

class TextIngestor:
    """
    A class for ingesting text data.
    """

    async def ingest_data(self, source: str) -> str:
        """
        Ingests text data from a source.

        Args:
            source: The source of the text data.

        Returns:
            The text data.
        """
        print(f"Ingesting text data from {source}...")
        await asyncio.sleep(1)  # Simulate I/O
        return "This is some sample text data."

    async def process_data(self, data: str) -> str:
        """
        Processes text data.

        Args:
            data: The text data to process.

        Returns:
            The processed text data.
        """
        print("Processing text data...")
        await asyncio.sleep(1)  # Simulate processing
        return data.lower()
