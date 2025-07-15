import asyncio

class AudioIngestor:
    """
    A class for ingesting audio data.
    """

    async def ingest_data(self, source: str) -> bytes:
        """
        Ingests audio data from a source.

        Args:
            source: The source of the audio data.

        Returns:
            The audio data.
        """
        print(f"Ingesting audio data from {source}...")
        await asyncio.sleep(1)  # Simulate I/O
        return b"This is some sample audio data."

    async def process_data(self, data: bytes) -> bytes:
        """
        Processes audio data.

        Args:
            data: The audio data to process.

        Returns:
            The processed audio data.
        """
        print("Processing audio data...")
        await asyncio.sleep(1)  # Simulate processing
        return data
